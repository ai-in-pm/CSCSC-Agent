# AI-Driven Earned Value Management (EVM) Agent

![CSCSC](https://github.com/user-attachments/assets/c98a1cb0-536f-449f-b61d-cfd1caa8b571)


## Overview

The EVM AI Agent is an intelligent system designed to automate and enhance project performance analysis using Earned Value Management methodologies. This agent combines EVM calculations with AI/ML analytics to provide real-time insights, forecasts, and natural language reporting for project managers and stakeholders. Designed as a "Physical AI" solution, it integrates with real-world project environments to deliver practical value across all areas of earned value management.

## Key Features

- **Core EVM Calculations**: Automated computation of standard EVM metrics (BCWS, BCWP, ACWP, CPI, SPI, etc.)
- **AI-Powered Analysis**: Advanced analytics for variance analysis, anomaly detection, and performance forecasting
- **Bayesian Predictive Forecasting**: Probabilistic time-series forecasting with confidence intervals for EV metrics
- **Multivariate Sensitivity Analysis**: Elasticity modeling to identify high-impact project parameters
- **Monte Carlo Simulation**: Stochastic project completion modeling with N=5000 simulation runs
- **Automated Risk Detection**: AI-driven identification and quantification of emergent project risks
- **Natural Language Generation**: Human-like explanations and commentary on project performance
- **Interactive Querying**: Chat-like interface for asking questions about project status and performance
- **Data Integration**: Connectors for popular project management tools (planned)
- **Compliant with DoD Standards**: Follows the 35 Cost/Schedule Control Systems Criteria (C/SCSC)

## Physical AI Capabilities

### Real-World Project Integration
- **On-site Data Collection**: Integration with mobile applications, IoT sensors, and manual inputs from physical project sites
- **Real-time Progress Tracking**: Analysis of physical progress through photo/video data, sensor readings, and on-site reporting
- **Site Visit Documentation**: Tools for documenting site inspections and linking observations to work breakdown structure elements

### Enhanced Decision Support
- **Risk Management**: Predictive analytics for identifying potential project risks based on EVM trends and physical conditions
- **Resource Optimization**: Algorithms for optimizing resource allocation based on actual physical progress and variance data
- **Corrective Action Recommendations**: Context-aware recommendations that account for physical project constraints

### Project Context Awareness
- **Environmental Factors Analysis**: Consideration of weather, location, and site conditions when analyzing variances
- **Supply Chain Integration**: Connections to supply chain systems to anticipate material delays and their impact
- **Labor Productivity Analysis**: Models that analyze workforce productivity factors in physical environments

### Environmental Impact Analysis
- Measures how weather, site conditions, and environmental factors affect project performance
- Provides quantified impact assessments on schedule and cost
- Generates actionable mitigation recommendations

### Supply Chain Management
- Evaluates the impact of material delays on project timeline
- Identifies critical path implications from supply chain disruptions
- Suggests procurement adjustments and mitigation strategies

### Site Observation Integration
- Reconciles reported progress with actual on-site observations
- Adjusts EVM metrics based on verified physical progress
- Improves accuracy of earned value calculations

### Risk Assessment
- Identifies at-risk work breakdown structure (WBS) elements based on current site conditions
- Monitors physical risk factors including weather, labor, equipment, and material availability
- Provides early warning indicators for potential issues

### IoT and Sensor Data Integration
- Incorporates readings from on-site IoT devices and sensors
- Monitors environmental conditions affecting project execution
- Tracks equipment utilization and maintenance status

## CrewAI Integration

The system incorporates a multi-agent collaborative framework using CrewAI, consisting of specialized agents:

- **Environmental Impact Analyst**: Analyzes how weather and site conditions affect project performance
- **Supply Chain Manager**: Evaluates material delays and procurement strategies
- **Site Progress Verifier**: Reconciles reported progress with actual site observations
- **Risk Assessment Specialist**: Identifies and quantifies physical risks to project execution
- **EVM Integration Specialist**: Synthesizes physical insights into EVM metrics

These agents work together in crews to perform complex analyses and generate comprehensive recommendations through structured task workflows.

### CrewAI Installation

Due to potential build issues with some CrewAI dependencies, two installation options are provided:

1. **Full Installation** - Requires Microsoft C++ Build Tools:
```bash
install_crewai.bat full
```

2. **Lightweight Installation** - Bypasses C++ dependency requirements:
```bash
install_crewai.bat lite
```

### CrewAI Demo

The system includes a demonstration script to showcase the CrewAI integration:

```bash
# Set your OpenAI API key (required)
set OPENAI_API_KEY=your-api-key-here

# Run the demo with all analysis types
python -m src.demo.crewai_demo

# Or run specific analysis types
python -m src.demo.crewai_demo --type environmental
python -m src.demo.crewai_demo --type supply_chain
python -m src.demo.crewai_demo --type site_progress
python -m src.demo.crewai_demo --type risk
```

### CrewAI API Endpoints

- `/api/v1/crewai/environmental-impact` - Analyze environmental impacts on project performance
- `/api/v1/crewai/supply-chain-impact` - Evaluate material delays and supply chain issues
- `/api/v1/crewai/site-progress-verification` - Verify and reconcile physical site progress
- `/api/v1/crewai/risk-assessment` - Assess physical project risks and suggest mitigations

## MPXJ Project File Integration

The CSCSC AI Agent now includes comprehensive support for project file format conversions and analysis through MPXJ integration, enabling seamless work with files from various project management software.

### Key MPXJ Features

- **Multi-Format Support**: Convert between numerous project file formats including Microsoft Project (MPP), Primavera P6 (XER), XML, MPX, and many more
- **Format Detection**: Automatic recognition of project file formats for efficient processing
- **Project Data Analysis**: Extract and analyze project data including tasks, resources, assignments, and critical path
- **Database Integration**: Import project data into the application database for further analysis
- **Interactive Visualization**: Visual representation of project metrics and resource allocation
- **Batch Processing**: Support for processing multiple project files simultaneously
- **User-Friendly Interface**: Drag-and-drop interface for uploading and converting project files
- **Comprehensive API**: RESTful API endpoints for programmatic access to MPXJ functionality

### Supported File Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| Microsoft Project | .mpp, .mpx, .xml | ✓ | ✓ |
| Primavera P6 | .xer, .pmxml | ✓ | ✓ |
| Asta Powerproject | .pp | ✓ | ✓ |
| Gantt Project | .gan | ✓ | ✓ |
| MSPDI XML | .xml | ✓ | ✓ |
| PMXML | .pmxml | ✓ | ✓ |
| Planner | .planner | ✓ | ✓ |
| Phoenix | .ppx | ✓ | - |
| ProjectLibre | .pod | ✓ | - |
| Synchro | .sp | ✓ | - |
| SDEF | .sdef | ✓ | ✓ |
| JSON | .json | ✓ | ✓ |

### Usage Examples

**Web Interface**:
- Access the project file converter through the web interface at `/mpxj`
- Upload project files via drag-and-drop or file browser
- Convert to desired format or analyze project data directly in the browser

**API Endpoints**:
- `/api/v1/mpxj/formats` - List all supported file formats
- `/api/v1/mpxj/upload` - Upload a project file
- `/api/v1/mpxj/convert/{filename}` - Convert a project file to a different format
- `/api/v1/mpxj/analyze/{filename}` - Analyze project data and return statistics
- `/api/v1/mpxj/import-to-database/{filename}` - Import project data to database

## Advanced Technical Features

### Bayesian Predictive Forecasting
- **Methodology**: Implements Bayesian Structural Time Series (BSTS) models for probabilistic forecasting of EVM metrics
- **Statistical Foundation**: Combines prior distributions with observed data to produce posterior predictive distributions
- **Uncertainty Quantification**: Generates confidence intervals (CI) at 95% confidence level for all forecasted values
- **Performance Metrics**: Reports forecast accuracy, RMSE (Root Mean Square Error), and MAE (Mean Absolute Error)
- **Temporal Components**: Decomposes time series into trend, seasonal, and cyclical components
- **Adaptive Learning**: Updates model parameters as new project data becomes available

### Multivariate Sensitivity Analysis
- **Elasticity Modeling**: Calculates elasticity coefficients to quantify the impact of parameter changes on project outcomes
- **Parameter Significance**: Ranks project parameters by their influence on Schedule Performance Index (SPI) and Cost Performance Index (CPI)
- **Scenario Simulation**: Evaluates positive and negative impact scenarios for each parameter
- **Decision Support**: Identifies high-leverage areas for management attention and resource allocation
- **Statistical Robustness**: Employs multivariate regression with regularization to handle correlated parameters

### Monte Carlo Simulation
- **Simulation Engine**: Utilizes Adaptive Stratified Sampling with Quasi-Monte Carlo integration techniques
- **Distribution Fitting**: Applies empirical and theoretical probability distributions to model uncertainty in project variables
- **Correlation Modeling**: Incorporates Pearson correlation coefficients to account for interdependencies between variables
- **Completion Analysis**: Generates P10, P50, P80, and P90 completion date estimates
- **Visualization**: Presents probability distribution of project completion timeframes
- **Computational Efficiency**: Optimized parallel processing allows 5,000+ simulation runs in seconds

### Automated Risk Detection
- **Risk Identification**: Employs pattern recognition algorithms to detect emerging risks from simulation results
- **Impact Assessment**: Quantifies potential impact of identified risks on project objectives
- **Confidence Scoring**: Assigns confidence levels to each identified risk based on statistical significance
- **Categorical Classification**: Categorizes risks as High, Medium, or Low impact with appropriate visualizations
- **Continuous Monitoring**: Updates risk profile as new project data becomes available
- **Integration**: Connects identified risks with sensitivity analysis to prioritize mitigation strategies

### Embedded Analytics Database
- **Persistent Storage**: SQLite-based embedded database for storing historical analysis results
- **Time Series Storage**: Optimized schema for EVM metrics and forecasts
- **Query Capabilities**: API for retrieving and analyzing historical predictions
- **Performance Tracking**: Evaluation of prediction accuracy over time
- **Cross-Project Analysis**: Ability to compare metrics across multiple projects

## Primavera P6 Integration

The CSCSC AI Agent now features comprehensive integration with Oracle Primavera P6, enabling advanced project data visualization, analysis, and AI-powered querying capabilities.

### Key Integration Features

- **Real-time Project Data Access**: Direct connection to Primavera P6 for retrieving up-to-date project information
- **Project Schedule Visualization**: Interactive Gantt chart visualization of project schedules imported from P6
- **Resource Allocation Analysis**: Visual representation of resource utilization across project activities
- **Progress S-Curve Analysis**: Comparison of planned vs. actual progress using S-curve visualization
- **AI-Powered Data Querying**: Natural language interface to query and analyze Primavera P6 project data
- **Critical Path Visualization**: Identification and visualization of critical path activities
- **Delay Analysis**: Automatic detection and impact assessment of delayed activities

### Technical Components

- **Primavera Connector**: API and database connectivity to Primavera P6 installation
- **Data Processor**: Transformation and analysis of project data for visualization and insights
- **Local Database**: SQLite storage of imported P6 data for offline analysis
- **Interactive Dashboard**: User-friendly interface for visualizing and querying project data

### Setup Instructions

1. Configure the Primavera P6 connection by setting the `P6_INSTALLATION_PATH` environment variable
2. Access the integration via the `/primavera` endpoint in the web interface
3. Import project data using the "Import Data" button in the interface
4. Select projects from the dropdown menu to view detailed visualizations
5. Use the AI query feature to ask questions about project data

### Technical Requirements

- **Oracle Primavera P6**: Professional or EPPM edition
- **Database Access**: Direct or API access to Primavera database
- **Environment Variable**: `P6_INSTALLATION_PATH` pointing to the Primavera installation directory

### Usage Examples

#### Example AI Queries
- "Show me all late activities in the current project"
- "What's the current progress of all projects?"
- "Which resources are overallocated?"
- "Show me the critical path for this project"
- "What's the forecasted completion date?"

## System Architecture

The system is built with a modular architecture that includes:

```
src/
├── main.py                 # Main application entry point
├── config/                 # Configuration settings
├── models/                 # Data models and schemas
├── data_ingestion/         # Data import and processing
├── evm_engine/             # Core EVM calculation engine
├── ai_ml_analysis/         # AI and ML analysis modules
├── nlg_engine/             # Natural Language Generation
├── user_interface/         # API and user interaction
├── crewai_integration/     # CrewAI multi-agent system
├── demo/                   # Demonstration scripts
└── utils/                  # Helper utilities
```

## Database

The agent uses an embedded SQLite database (evm_agent.db) to store project data, EVM metrics, forecasts, and user interactions. The database schema includes tables for:

- Projects
- Tasks
- EVM Metrics
- Forecasts
- Variance Explanations
- Physical Project Data
- Site Observations
- Environmental Factors

## Getting Started

### Prerequisites

- Python 3.8+ (Developed with Python 3.13.2)
- Virtual environment (recommended)
- OpenAI API key (required for CrewAI functionality)
- Microsoft C++ Build Tools (optional, for full CrewAI installation)

### Installation

1. Clone the repository
2. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/MacOS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Start the API server:

```bash
python -m src.main
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `/api/v1/chat` - Chat with the EVM AI agent
- `/api/v1/projects` - List all projects
- `/api/v1/projects/{project_id}` - Get project details
- `/api/v1/projects/{project_id}/metrics` - Get project EVM metrics
- `/api/v1/projects/{project_id}/forecast` - Get project forecast
- `/api/v1/tasks/{task_id}/metrics` - Get task EVM metrics

## Example Queries

The agent can respond to natural language queries such as:

- "What is the current status of project P001?"
- "Why is task T002 over budget?"
- "What is the forecast completion date for the construction project?"
- "Recommend actions to improve the schedule performance of project P003"
- "How has the recent weather affected our construction schedule?"
- "Which WBS elements are most at risk based on current site conditions?"
- "What impact will the delayed concrete delivery have on our critical path?"

## Real-World Applications

The EVM AI Agent is designed for deployment in various physical project environments:

- **Construction Projects**: Monitoring progress, costs, and schedules for building projects
- **Manufacturing**: Tracking production lines and assembly processes against planned values
- **Infrastructure Development**: Managing large-scale infrastructure projects with complex dependencies
- **Defense Acquisitions**: Supporting DoD compliant earned value management for defense contracts
- **Energy Sector**: Monitoring oil, gas, and renewable energy installation projects

## Future Enhancements

- Integration with JIRA, Microsoft Project, and SAP
- Enhanced visualization of EVM metrics and trends
- Mobile application for on-the-go access
- Advanced risk analysis and Monte Carlo simulations
- Augmented reality (AR) interfaces for on-site EVM visualization
- Expanded IoT sensor integration for automated data collection
- Machine learning models for anomaly detection in physical progress

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
