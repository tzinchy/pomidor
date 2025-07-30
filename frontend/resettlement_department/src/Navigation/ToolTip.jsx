const ToolTip = ({text}) => {
    return (
    
    <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2
                    px-3 py-1.5 text-xs text-gray-600
                    rounded-lg border border-white/20
                    bg-white/10 backdrop-blur-md shadow-lg
                    opacity-0 group-hover:opacity-100
                    transition pointer-events-none z-1000 whitespace-nowrap">
    {text}
    {/* Tooltip справа */}
    </div>
    );
};

export default ToolTip;