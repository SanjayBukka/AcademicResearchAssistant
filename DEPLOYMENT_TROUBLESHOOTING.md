# 🔧 Deployment Troubleshooting Guide

## 🚨 Common Deployment Issues & Solutions

### Issue 1: PyTorch Version Compatibility Error
**Error**: `Could not find a version that satisfies the requirement torch>=2.1.0,<2.2.0`

**Solution**: 
```bash
# Use the updated requirements.txt with torch>=2.0.0
# Or try the minimal requirements for faster deployment:
cp requirements-minimal.txt requirements.txt
```

### Issue 2: Python Version Compatibility
**Error**: `Requires-Python` version conflicts

**Solutions**:
1. **Use Streamlit-optimized requirements**:
   ```bash
   cp requirements-streamlit.txt requirements.txt
   ```

2. **Use minimal requirements** (fastest deployment):
   ```bash
   cp requirements-minimal.txt requirements.txt
   ```

3. **Specify Python version** in runtime.txt:
   ```bash
   echo "python-3.11" > runtime.txt
   ```

### Issue 3: Large Dependencies Timeout
**Error**: Installation timeout or memory issues

**Solutions**:
1. **Use minimal requirements**:
   ```bash
   cp requirements-minimal.txt requirements.txt
   ```

2. **Remove heavy dependencies** temporarily:
   - Comment out `torch`, `transformers`, `sentence-transformers`
   - Deploy basic version first
   - Add features incrementally

### Issue 4: System Dependencies Missing
**Error**: Missing system packages

**Solution**: Ensure `packages.txt` exists with:
```
freeglut3-dev
libgtk2.0-dev
```

## 🎯 Quick Fix Strategies

### Strategy 1: Minimal Deployment (Fastest)
```bash
# Use minimal requirements
cp requirements-minimal.txt requirements.txt
git add requirements.txt
git commit -m "Use minimal requirements for deployment"
git push
```

### Strategy 2: Streamlit Cloud Optimized
```bash
# Use Streamlit-optimized requirements
cp requirements-streamlit.txt requirements.txt
git add requirements.txt
git commit -m "Optimize for Streamlit Cloud"
git push
```

### Strategy 3: Gradual Feature Addition
1. Start with minimal requirements
2. Deploy successfully
3. Add features one by one
4. Test each addition

## 🔍 Debugging Steps

### 1. Check Logs
- Look for specific error messages
- Identify which package is causing issues
- Note Python version being used

### 2. Test Locally
```bash
# Create clean environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Verify Dependencies
```bash
# Check if packages install correctly
pip install torch>=2.0.0
pip install sentence-transformers>=2.2.2
```

## 📋 Platform-Specific Solutions

### Streamlit Cloud
- Use `requirements-streamlit.txt`
- Add `packages.txt` for system dependencies
- Set Python version in Advanced Settings

### Heroku
- Add `runtime.txt` with Python version
- Use `requirements-minimal.txt` for faster builds
- Increase build timeout if needed

### Railway/Render
- Use standard `requirements.txt`
- Monitor build logs for specific errors
- Consider using Docker for complex dependencies

## 🚀 Emergency Deployment (Minimal Features)

If you need to deploy immediately with basic functionality:

```bash
# 1. Use minimal requirements
cp requirements-minimal.txt requirements.txt

# 2. Commit and push
git add .
git commit -m "Emergency deployment with minimal features"
git push

# 3. Features available with minimal setup:
# ✅ Basic UI and navigation
# ✅ Reference finder (limited)
# ✅ Writing assistant (with Gemini)
# ✅ Basic paper summarization
# ❌ Advanced ML features
# ❌ Embedding-based search
# ❌ Research gap analysis
```

## 🔄 Gradual Feature Restoration

After successful minimal deployment:

1. **Add torch and transformers**:
   ```
   torch>=2.0.0
   transformers>=4.30.0
   ```

2. **Add sentence transformers**:
   ```
   sentence-transformers>=2.2.2
   ```

3. **Add vector storage**:
   ```
   faiss-cpu>=1.7.4
   ```

4. **Add remaining features**:
   ```
   keybert>=0.9.0
   nltk>=3.9.1
   ```

## 📞 Getting Help

1. **Check deployment logs** for specific error messages
2. **Try minimal requirements** first
3. **Test locally** with the same Python version
4. **Use platform-specific requirements** files
5. **Contact platform support** if issues persist

## ✅ Success Indicators

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Application starts successfully
- ✅ Health check passes
- ✅ Basic features work
- ✅ No critical runtime errors
