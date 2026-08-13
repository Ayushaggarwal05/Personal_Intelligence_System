import React from "react";
import { AstaCinematicIntro } from "./AstaCinematicIntro";

interface ActivationScreenProps {
  onComplete: () => void;
}

export const ActivationScreen: React.FC<ActivationScreenProps> = ({ onComplete }) => {
  return <AstaCinematicIntro onComplete={onComplete} />;
};
