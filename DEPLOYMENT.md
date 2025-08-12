# Academic Research Assistant - Deployment Guide

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.7 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### 2. Installation

```bash
# Clone or download the project
cd AcademicResearchAssistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

#### Option A: Environment Variables (Recommended for deployment)
```bash
# Create a .env file
cp .env.example .env

# Edit .env and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

#### Option B: Manual Entry
- The application will prompt for API key in the sidebar
- Enter your Gemini API key when using Writing Guidance or Q&A features

### 4. Run the Application

#### Fast Startup (Recommended)
```bash
streamlit run run_fast.py
```

#### Standard Startup
```bash
streamlit run main.py
```

The application will be available at `http://localhost:8502`

## ⚡ Performance Optimization

### Model Speed Options
- **Fast Mode** (~90MB): Quick loading, good performance
- **Balanced Mode** (~420MB): Better accuracy, moderate loading
- **Accurate Mode** (~440MB): Best for academic content, slower loading

### Performance Tips
1. **First Run**: May take 1-2 minutes to download models
2. **Subsequent Runs**: Much faster due to caching
3. **Keep Running**: Avoid restarting to maintain cached models
4. **Use Fast Mode**: Select "fast" in performance settings for quicker responses

## 🌐 Cloud Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your `GEMINI_API_KEY` in the Secrets section
4. Deploy!

### Heroku
1. Create a `Procfile`:
   ```
   web: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Set environment variable:
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key
   ```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8502

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
```

## 🔧 Configuration Options

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Default model (default: gemini-pro)
- `TESSERACT_CMD`: Path to Tesseract OCR executable

### Features
- **Reference Finding**: Search academic papers from multiple sources
- **Writing Guidance**: AI-powered writing assistance
- **Paper Summarization**: Automatic paper summarization
- **Research Gap Analysis**: Identify research opportunities
- **Q&A System**: Ask questions about uploaded papers

## 📋 System Requirements

### Core Dependencies
- streamlit
- google-generativeai
- requests
- pandas
- numpy
- scikit-learn
- transformers
- torch
- sentence-transformers

### Optional (for enhanced features)
- pytesseract (OCR)
- pdf2image (PDF to image conversion)
- Tesseract OCR (system installation)

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider rate limiting for production deployments
- Monitor API usage and costs

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Ensure your Gemini API key is valid and has proper permissions
2. **OCR Not Working**: Install Tesseract OCR system package
3. **Memory Issues**: Consider using CPU-only versions of ML models for deployment

### Support
- Check the application logs for detailed error messages
- Ensure all dependencies are properly installed
- Verify internet connectivity for API calls
