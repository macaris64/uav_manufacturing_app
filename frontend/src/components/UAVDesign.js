import React from 'react';

const UAVDesign = ({ parts }) => {
    const fullColor = 'darkgreen';
    const patternColor = 'url(#checker-pattern)';

    const getPartColor = (partName) => {
        return Array.isArray(parts) && parts.some(part => part.name === partName) ? fullColor : patternColor;
    };

    return (
        <svg id="combat-uav" viewBox="0 0 200 200" style={{ width: '300px', height: '300px' }}>
            <defs>
                <pattern id="checker-pattern" width="10" height="10" patternUnits="userSpaceOnUse">
                    <rect width="5" height="5" fill="lightgray" />
                    <rect x="5" y="5" width="5" height="5" fill="lightgray" />
                    <rect x="5" width="5" height="5" fill="white" />
                    <rect y="5" width="5" height="5" fill="white" />
                </pattern>
            </defs>

            {/* Body */}
            <rect className="body" x="95" y="40" width="10" height="80" fill={getPartColor("BODY")} />

            {/* Left Wing */}
            <polygon className="wing-left" points="20,80 95,70 95,90" fill={getPartColor("WING")} />

            {/* Right Wing */}
            <polygon className="wing-right" points="105,70 105,90 180,80" fill={getPartColor("WING")} />

            {/* Tail */}
            <rect className="tail" x="97" y="120" width="6" height="30" fill={getPartColor("TAIL")} />
            <polygon className="tail-wing" points="85,130 115,130 100,150" fill={getPartColor("TAIL")} />

            {/* Avionics */}
            <ellipse className="avionics" cx="100" cy="35" rx="5" ry="10" fill={getPartColor("AVIONICS")} />

            {/* Left Propeller */}
            <line className="propeller-left" x1="20" y1="80" x2="10" y2="80" stroke="black" strokeWidth="2" />
            <line className="propeller-left" x1="15" y1="75" x2="15" y2="85" stroke="black" strokeWidth="2" />

            {/* Right Propeller */}
            <line className="propeller-right" x1="180" y1="80" x2="190" y2="80" stroke="black" strokeWidth="2" />
            <line className="propeller-right" x1="185" y1="75" x2="185" y2="85" stroke="black" strokeWidth="2" />
        </svg>
    );
};

export default UAVDesign;
