import React from 'react';
export default function DiffBlock({diff}){
  return (
    <pre className='diff-box'>
      {diff.split('\n').map((l,i)=>(
        <div key={i} className={l.startsWith('+')?'diff-add':l.startsWith('-')?'diff-remove':'diff-normal'}>{l}</div>
      ))}
    </pre>
  );
}