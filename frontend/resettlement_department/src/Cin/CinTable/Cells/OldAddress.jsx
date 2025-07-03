export default function OldAddress( props ){
  const value = props['props']
  
  return (
    <div className="flex w-full flex-row items-center justify-start gap-1">
      <div className="flex flex-1 flex-col items-start justify-start min-w-0">
        <div className="whitespace-normal break-words">
          {value['old_address']}
        </div>
      </div>
    </div>
  );
  }