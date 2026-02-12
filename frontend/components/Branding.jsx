
import React from "react";


export const PracticeRoomLogo = ({ className = "text-lg", logoSize = "h-8", variant = "horizontal" }) => {
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
            <div className="h-6 w-px bg-slate-200" />
            <PracticeRoomText className={className} />
        </div>
    );
};

export const PracticeRoomText = ({ className = "text-lg" }) => {
    return (
        <span className={`${className} font-bold text-slate-700 tracking-tight leading-none`}>
            Practice <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 animate-gradient-x">Room</span>
        </span>
    );
};

