import React from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import ReportSection from '../components/ReportSection';
export default function Result(){
  const {state}=useLocation();
  
  if(!state?.updatedRepo || !state?.changeReport){
    return <Navigate to='/' replace />;
  }
  
  return (
    <div className='container'>
      <h2>Updated Repo Link</h2>
      <a href={state.updatedRepo} target='_blank'>{state.updatedRepo}</a>
      <h2>Change Report</h2>
      <ReportSection report={state.changeReport}/>
    </div>
  );
}