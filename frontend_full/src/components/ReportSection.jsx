import React from 'react';
import DiffBlock from './DiffBlock';
export default function ReportSection({report}){
  return (
    <div>
      {report.map((r,i)=>(
        <div key={i} className='report-box'>
          <h3>{r.file}</h3>
          <h4>Issues Fixed:</h4>
          <ul>{r.issues_fixed.map((x,j)=><li key={j}>{x}</li>)}</ul>
          <h4>Code Diff:</h4>
          <DiffBlock diff={r.diff}/>
        </div>
      ))}
    </div>
  );
}