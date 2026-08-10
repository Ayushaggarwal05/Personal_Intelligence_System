const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];
if (!filePath) {
    console.error("Error: No file path provided.");
    process.exit(1);
}

try {
    const code = fs.readFileSync(filePath, 'utf-8');
    const symbols = parseCode(code, filePath);
    console.log(JSON.stringify(symbols, null, 2));
} catch (err) {
    console.error("Parser failed: " + err.message);
    process.exit(1);
}

function findModule(moduleName, startPath) {
    let current = path.dirname(startPath);
    while (true) {
        const potential = path.join(current, 'node_modules', moduleName);
        if (fs.existsSync(potential)) {
            return potential;
        }
        const parent = path.dirname(current);
        if (parent === current) {
            break;
        }
        current = parent;
    }
    // Check standard project paths as fallback
    const projectRoot = path.resolve(__dirname, '../../../../');
    const fallbackPaths = [
        path.join(projectRoot, 'frontend', 'node_modules', moduleName),
        path.join(projectRoot, 'node_modules', moduleName)
    ];
    for (const p of fallbackPaths) {
        if (fs.existsSync(p)) return p;
    }
    return null;
}

function parseCode(code, filePath) {
    // 1. Try Babel Parser (Highly robust for JSX/TSX)
    const babelPath = findModule('@babel/parser', filePath);
    if (babelPath) {
        try {
            const parser = require(babelPath);
            const ast = parser.parse(code, {
                sourceType: "module",
                plugins: ["jsx", "typescript", "classProperties", "decorators-legacy", "dynamicImport"]
            });
            return walkBabelAST(ast, code);
        } catch (e) {
            // Fall back to TS compiler if Babel fails
        }
    }

    // 2. Try TypeScript Parser
    const tsPath = findModule('typescript', filePath);
    if (tsPath) {
        try {
            const ts = require(tsPath);
            const sourceFile = ts.createSourceFile(filePath, code, ts.ScriptTarget.Latest, true);
            return walkTypeScriptAST(sourceFile, ts, code);
        } catch (e) {
            // Let the caller handle failure and run Regex fallback
        }
    }

    throw new Error("No parser found in node_modules (@babel/parser or typescript).");
}

function getLineFromPos(code, pos) {
    let line = 1;
    for (let i = 0; i < pos; i++) {
        if (code[i] === '\n') line++;
    }
    return line;
}

function walkBabelAST(ast, code) {
    const symbols = [];
    
    function traverse(node) {
        if (!node) return;

        // 1. Classes
        if (node.type === 'ClassDeclaration' && node.id) {
            const lineStart = getLineFromPos(code, node.start);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.append = symbols.push({
                name: node.id.name,
                type: "class",
                signature: `class ${node.id.name}`,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 2. Functions (Standard)
        if (node.type === 'FunctionDeclaration' && node.id) {
            const name = node.id.name;
            const params = (node.params || []).map(p => p.type === 'Identifier' ? p.name : '{}').join(', ');
            const sig = `function ${name}(${params})`;
            const lineStart = getLineFromPos(code, node.start);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.push({
                name: name,
                type: "function",
                signature: sig,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 3. Arrow / Assigned Functions
        if (node.type === 'VariableDeclarator' && node.id && node.id.type === 'Identifier') {
            const init = node.init;
            if (init && (init.type === 'ArrowFunctionExpression' || init.type === 'FunctionExpression')) {
                const name = node.id.name;
                const params = (init.params || []).map(p => p.type === 'Identifier' ? p.name : '{}').join(', ');
                const sig = `const ${name} = (${params}) =>`;
                const lineStart = getLineFromPos(code, node.start);
                const lineEnd = getLineFromPos(code, node.end);
                symbols.push({
                    name: name,
                    type: "function",
                    signature: sig,
                    docstring: "",
                    line_start: lineStart,
                    line_end: lineEnd
                });
            }
        }

        // 4. Class Methods
        if (node.type === 'ClassMethod' && node.key && node.key.type === 'Identifier') {
            const name = node.key.name;
            const params = (node.params || []).map(p => p.type === 'Identifier' ? p.name : '{}').join(', ');
            const sig = `${name}(${params})`;
            const lineStart = getLineFromPos(code, node.start);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.push({
                name: name,
                type: "function",
                signature: sig,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 5. Express Routes
        if (node.type === 'CallExpression' && node.callee && node.callee.type === 'MemberExpression') {
            const callee = node.callee;
            if (callee.object && callee.object.type === 'Identifier' && callee.property && callee.property.type === 'Identifier') {
                const obj = callee.object.name;
                const method = callee.property.name;
                if ((obj === 'app' || obj === 'router' || obj === 'route') && ['get', 'post', 'put', 'delete', 'patch', 'use'].includes(method)) {
                    const arg0 = node.arguments[0];
                    if (arg0 && (arg0.type === 'StringLiteral' || arg0.type === 'Literal')) {
                        const pathVal = arg0.value;
                        const lineStart = getLineFromPos(code, node.start);
                        symbols.push({
                            name: `${method.toUpperCase()} ${pathVal}`,
                            type: "route",
                            signature: `[${method.toUpperCase()}] ${pathVal}`,
                            docstring: "",
                            line_start: lineStart,
                            line_end: lineStart
                        });
                    }
                }
            }
        }

        // Traverse children
        for (const key in node) {
            const child = node[key];
            if (child && typeof child === 'object') {
                if (Array.isArray(child)) {
                    child.forEach(c => traverse(c));
                } else if (child.type) {
                    traverse(child);
                }
            }
        }
    }

    traverse(ast.program);
    return symbols;
}

function walkTypeScriptAST(sourceFile, ts, code) {
    const symbols = [];
    
    function visit(node) {
        // 1. Classes
        if (ts.isClassDeclaration(node) && node.name) {
            const lineStart = getLineFromPos(code, node.pos);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.push({
                name: node.name.text,
                type: "class",
                signature: `class ${node.name.text}`,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 2. Functions (Standard)
        if (ts.isFunctionDeclaration(node) && node.name) {
            const lineStart = getLineFromPos(code, node.pos);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.push({
                name: node.name.text,
                type: "function",
                signature: `function ${node.name.text}()`,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 3. Arrow / Assigned Functions
        if (ts.isVariableDeclaration(node) && node.name && ts.isIdentifier(node.name)) {
            if (node.initializer && (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
                const lineStart = getLineFromPos(code, node.pos);
                const lineEnd = getLineFromPos(code, node.end);
                symbols.push({
                    name: node.name.text,
                    type: "function",
                    signature: `const ${node.name.text} = () =>`,
                    docstring: "",
                    line_start: lineStart,
                    line_end: lineEnd
                });
            }
        }

        // 4. Method Declarations
        if (ts.isMethodDeclaration(node) && node.name && ts.isIdentifier(node.name)) {
            const lineStart = getLineFromPos(code, node.pos);
            const lineEnd = getLineFromPos(code, node.end);
            symbols.push({
                name: node.name.text,
                type: "function",
                signature: `${node.name.text}()`,
                docstring: "",
                line_start: lineStart,
                line_end: lineEnd
            });
        }

        // 5. Express Routes
        if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
            const propAccess = node.expression;
            if (ts.isIdentifier(propAccess.expression) && ts.isIdentifier(propAccess.name)) {
                const obj = propAccess.expression.text;
                const method = propAccess.name.text;
                if ((obj === 'app' || obj === 'router' || obj === 'route') && ['get', 'post', 'put', 'delete', 'patch', 'use'].includes(method)) {
                    const arg0 = node.arguments[0];
                    if (arg0 && ts.isStringLiteral(arg0)) {
                        const pathVal = arg0.text;
                        const lineStart = getLineFromPos(code, node.pos);
                        symbols.push({
                            name: `${method.toUpperCase()} ${pathVal}`,
                            type: "route",
                            signature: `[${method.toUpperCase()}] ${pathVal}`,
                            docstring: "",
                            line_start: lineStart,
                            line_end: lineStart
                        });
                    }
                }
            }
        }

        ts.forEachChild(node, visit);
    }

    visit(sourceFile);
    return symbols;
}
