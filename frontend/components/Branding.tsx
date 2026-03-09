
import React from "react";

interface PracticeRoomLogoProps {
  className?: string;
  logoSize?: string;
  variant?: "horizontal" | "vertical";
}

export const PracticeRoomLogo: React.FC<PracticeRoomLogoProps> = ({ className = "text-lg", logoSize = "h-8", variant = "horizontal" }) => {
    if (variant === "vertical") {
        return (
            <div className="flex flex-col items-center text-center">
                <img src="/assets/logo.png" alt="Codebasics" className={`${logoSize} w-auto drop-shadow-sm mb-4`} />
                <PracticeRoomText className={className} />
            </div>
        );
    }

    return (
        <div className="flex items-center gap-5">
            <img src="/assets/logo.png" alt="Codebasics" className={`${logoSize} w-auto drop-shadow-sm`} />
            <div className="h-6 w-px bg-border" />
            <PracticeRoomText className={className} />
        </div>
    );
};

interface PracticeRoomTextProps {
  className?: string;
}

export const PracticeRoomText: React.FC<PracticeRoomTextProps> = ({ className = "text-lg" }) => {
    return (
        <span className={`${className} font-display font-bold text-foreground tracking-tight leading-none uppercase`}>
            Practice <span className="text-cb-lime">Room</span>
        </span>
    );
};
