import React from 'react';
import UploadForm from '../components/UploadForm';

export default function Home() {
  return (
    <div className='container'>
      <div className='header'>
        <h1>🤖 AI Code Review Agent</h1>
        <p>Automated code analysis, issue detection, and intelligent fixes powered by AI</p>
        
        <div className='features'>
          <div className='feature'>
            <div className='feature-icon'>🔍</div>
            <h3>Smart Analysis</h3>
            <p>AI-powered code scanning</p>
          </div>
          <div className='feature'>
            <div className='feature-icon'>🛠️</div>
            <h3>Auto Fixes</h3>
            <p>Intelligent code corrections</p>
          </div>
          <div className='feature'>
            <div className='feature-icon'>📊</div>
            <h3>Detailed Reports</h3>
            <p>Comprehensive change tracking</p>
          </div>
          <div className='feature'>
            <div className='feature-icon'>🚀</div>
            <h3>GitHub Integration</h3>
            <p>Seamless repository updates</p>
          </div>
        </div>
      </div>
      
      <UploadForm />
    </div>
  );
}