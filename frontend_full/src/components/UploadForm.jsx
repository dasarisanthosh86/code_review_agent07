import React,{useState} from 'react';
import {reviewCode} from '../api';
import {useNavigate} from 'react-router-dom';
export default function UploadForm(){
  const [repo,setRepo]=useState('');
  const [file,setFile]=useState(null);
  const [githubToken,setGithubToken]=useState('');
  const [loading,setLoading]=useState(false);
  const [progress,setProgress]=useState('');
  const [error,setError]=useState('');
  const nav=useNavigate();
  
  const submit=async e=>{
    e.preventDefault();
    if(!repo.trim()){
      setError('Please enter a repository URL');
      return;
    }
    
    const githubUrlPattern = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    if(!githubUrlPattern.test(repo.trim())){
      setError('Please enter a valid GitHub repository URL');
      return;
    }
    
    if(!file){
      setError('Please upload a scan report JSON file');
      return;
    }
    
    if(!githubToken.trim()){
      setError('Please enter your GitHub token to push fixes');
      return;
    }
    
    setLoading(true);
    setError('');
    setProgress('🔄 Starting review process...');
    
    try{
      console.log('Sending request:', repo, file, githubToken ? 'Token provided' : 'No token');
      const res=await reviewCode(repo,file,githubToken);
      console.log('Response:', res);
      
      setTimeout(()=>{
        nav('/result',{state:{updatedRepo:res.updated_repo_link,changeReport:res.change_report}});
      },1000);
    }catch(err){
      console.error('Error details:', err);
      setError(err.message || 'Review failed');
      setLoading(false);
      setProgress('');
    }
  };
  
  return (
    <form className='form-box' onSubmit={submit}>
      <label>GitHub Repo URL *</label>
      <input 
        value={repo} 
        onChange={e=>setRepo(e.target.value)}
        placeholder='https://github.com/user/repo'
        disabled={loading}
      />
      
      <label>GitHub Token *</label>
      <input 
        type='password'
        value={githubToken} 
        onChange={e=>setGithubToken(e.target.value)}
        placeholder='ghp_xxxxxxxxxxxx'
        disabled={loading}
        required
      />
      
      <label>Scan Report *</label>
      <input 
        type='file' 
        onChange={e=>setFile(e.target.files[0])}
        accept='.json'
        disabled={loading}
        required
      />
      
      {error && <div className='error'>❌ {error}</div>}
      
      {loading && (
        <div className='progress'>
          <div className='spinner'></div>
          <div className='progress-text'>{progress}</div>
        </div>
      )}
      
      <button type='submit' disabled={loading}>
        {loading ? 'Processing...' : 'Start Review'}
      </button>
    </form>
  );
}