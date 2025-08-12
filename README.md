# 🎓 Academic Research Assistant

A comprehensive AI-powered research tool that helps academics and researchers with paper discovery, writing assistance, summarization, and research gap analysis.

## ✨ Features

- **🔍 Smart Reference Finder**: Discover relevant papers from arXiv, Semantic Scholar, and CrossRef
- **✍️ AI Writing Assistant**: Get intelligent guidance for academic writing with Gemini AI
- **📄 Paper Summarizer**: Generate section-wise summaries of research papers
- **🕳️ Research Gap Analyzer**: Identify unexplored research opportunities
- **💬 Q&A Assistant**: Upload papers and ask questions with contextual answers

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd AcademicResearchAssistant

# Run the deployment script
python deploy.py
```

### Option 2: Manual Setup
```bash
# Clone the repository
git clone <repository-url>
cd AcademicResearchAssistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the application
streamlit run main.py
```

## 🌐 Deployment Options

### 1. Streamlit Cloud (Easiest)
1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add your `GEMINI_API_KEY` in the Secrets section
5. Deploy!

### 2. Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_api_key

# Deploy
git push heroku main
```

### 3. Docker
```bash
# Build the image
docker build -t academic-research-assistant .

# Run with environment variables
docker run -p 8502:8502 -e GEMINI_API_KEY=your_api_key academic-research-assistant

# Or use docker-compose
docker-compose up
```

### 4. Railway
1. Connect your GitHub repository to [Railway](https://railway.app)
2. Add `GEMINI_API_KEY` environment variable
3. Deploy automatically

### 5. Render
1. Connect your repository to [Render](https://render.com)
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variable `GEMINI_API_KEY`

## ⚙️ Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `GEMINI_MODEL`: Model to use (default: gemini-pro)
- `PERFORMANCE_MODE`: fast/balanced/accurate (default: fast)
- `MAX_PAPERS_DISPLAY`: Maximum papers to display (default: 20)

### Performance Modes
- **Fast** (~90MB): Quick loading, good performance
- **Balanced** (~420MB): Better accuracy, moderate loading  
- **Accurate** (~440MB): Best for academic content, slower loading

## 📁 Project Structure
```
AcademicResearchAssistant/
├── main.py                 # Main application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── deploy.py             # Deployment script
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── Procfile              # Heroku configuration
├── .env.example          # Environment template
├── features/             # Feature modules
│   ├── references/       # Reference finder
│   ├── writing/          # Writing assistant
│   ├── summarizer/       # Paper summarizer
│   ├── gap_finder/       # Research gap analyzer
│   └── question/         # Q&A assistant
└── utils/                # Utility functions
```

## 🔧 Development

### Local Development
```bash
# Install in development mode
pip install -e .

# Run with hot reload
streamlit run main.py --server.runOnSave=true
```

### Adding New Features
1. Create a new module in `features/`
2. Add the feature to the navigation in `main.py`
3. Update configuration if needed

## 🔒 Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider rate limiting for production deployments
- Monitor API usage and costs

## 🐛 Troubleshooting

### Common Deployment Issues
1. **PyTorch Version Error**: Use `requirements-minimal.txt` for faster deployment
2. **Python Version Conflicts**: Try `requirements-streamlit.txt` for Streamlit Cloud
3. **Installation Timeout**: Use minimal requirements first, add features gradually
4. **API Key Error**: Ensure your Gemini API key is valid and set correctly

### Quick Fixes
```bash
# For deployment issues, try minimal requirements:
cp requirements-minimal.txt requirements.txt

# For Streamlit Cloud specifically:
cp requirements-streamlit.txt requirements.txt
```

### Getting Help
- Check `DEPLOYMENT_TROUBLESHOOTING.md` for detailed solutions
- Review application logs for specific error messages
- Test locally with the same Python version as deployment platform
- Use minimal requirements for emergency deployment

## 📊 System Requirements

### Minimum
- Python 3.7+
- 2GB RAM
- 1GB storage

### Recommended
- Python 3.9+
- 4GB RAM
- 2GB storage
- Good internet connection

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the deployment documentation
