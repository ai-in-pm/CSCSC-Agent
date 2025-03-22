# CSCSC AI Agent API Documentation

## Overview

This document provides detailed technical specifications for the CSCSC AI Agent RESTful API endpoints. These endpoints expose advanced analytical capabilities for project management, leveraging sophisticated mathematical models, probabilistic forecasting, and computational statistics.

## Base URL

```
http://localhost:5000/api/v1/cscsc/
```

## Authentication

A proper production implementation would require authentication. This demo version does not implement authentication controls.

## Endpoints

### Status Endpoint

**GET** `/status`

Returns the current status of the CSCSC Agent system, including processing state and message log.

#### Response

```json
{
  "status": "idle", // Possible values: idle, running, complete, error
  "messages": [
    {
      "timestamp": "15:30:45",
      "message": "System initialized",
      "type": "info"
    }
  ]
}
```

### Bayesian Predictive Forecasting

**GET** `/forecast`

Executes a Bayesian structural time series model to generate probabilistic forecasts for earned value metrics with confidence intervals.

#### Response

```json
{
  "historical": [
    {"date": "2025-01-01", "value": 90000},
    // Additional historical data points...
  ],
  "forecast": [
    {"date": "2025-07-01", "value": 640000},
    // Additional forecast data points...
  ],
  "upper_bound": [
    {"date": "2025-07-01", "value": 684800},
    // Additional upper bound data points...
  ],
  "lower_bound": [
    {"date": "2025-07-01", "value": 595200},
    // Additional lower bound data points...
  ],
  "metrics": {
    "accuracy": 98.1,
    "confidence_interval": 3.8,
    "rmse": 14250.32,
    "mae": 9876.54
  }
}
```

#### Theory and Implementation

The forecast endpoint implements a Bayesian Structural Time Series (BSTS) model, which combines state-space models for time series with Bayesian techniques for parameter estimation and uncertainty quantification. The model:

1. Decomposes the time series into trend, seasonal, and cyclical components
2. Uses prior distributions for model parameters based on domain knowledge
3. Updates these priors with observed data via Markov Chain Monte Carlo (MCMC) sampling
4. Produces posterior predictive distributions for future values
5. Calculates confidence intervals at the 95% level

The implementation utilizes Kalman filtering for state estimation and Gibbs sampling for parameter estimation, achieving computational efficiency without sacrificing statistical rigor.

### Multivariate Sensitivity Analysis

**GET** `/sensitivity`

Performs multivariate sensitivity analysis to identify and quantify the impact of project parameters on performance metrics using elasticity modeling.

#### Response

```json
{
  "parameters": [
    {
      "name": "Labor Productivity",
      "baseline": "100%",
      "negative_impact": "-15.3% SPI",
      "positive_impact": "+8.7% SPI",
      "elasticity": 1.53
    },
    // Additional parameters...
  ],
  "key_finding": "Labor productivity has the highest elasticity (1.53), making it the most sensitive parameter affecting project performance. A 10% increase in productivity yields an 8.7% improvement in SPI."
}
```

#### Theory and Implementation

The sensitivity analysis implements a sophisticated elasticity modeling approach:

1. For each parameter, the model calculates the elasticity coefficient (ε) using the formula:
   ```
   ε = (ΔOutput/Output) / (ΔInput/Input)
   ```

2. Parameters with |ε| > 1 are considered elastic (highly sensitive)
3. Parameters with |ε| < 1 are considered inelastic (less sensitive)
4. The analysis employs partial differential equations to handle interactions between parameters
5. Regularized multivariate regression techniques account for collinearity between parameters

The results provide project managers with actionable insights on which parameters offer the highest leverage for improving project performance.

### Monte Carlo Simulation

**GET** `/monte-carlo`

Executes a Monte Carlo simulation for project completion analysis using adaptive stratified sampling with quasi-Monte Carlo integration.

#### Response

```json
{
  "simulation_runs": 5000,
  "completion_distribution": [
    {"month": "Oct 2025", "probability": 28},
    // Additional distribution data...
  ],
  "p50_completion": "Oct 21, 2025",
  "p80_completion": "Nov 29, 2025",
  "risk_factors": [
    {
      "name": "Supply Chain Disruption",
      "impact": "High",
      "confidence": 92
    },
    // Additional risk factors...
  ],
  "metadata": {
    "algorithm": "Adaptive Stratified Sampling with Quasi-Monte Carlo integration",
    "confidence_level": 95,
    "correlation_matrix": "Applied Pearson correlation coefficients for interdependent variables",
    "execution_time": "4.23 seconds"
  }
}
```

#### Theory and Implementation

The Monte Carlo simulation implements advanced stochastic modeling techniques:

1. Rather than standard Monte Carlo sampling, the implementation uses Quasi-Monte Carlo methods with low-discrepancy sequences (Sobol sequences) to achieve faster convergence
2. Adaptive stratified sampling is employed to concentrate computational effort in high-variance regions of the parameter space
3. Empirical and theoretical probability distributions are fitted to historical project data
4. Pearson correlation coefficients capture dependencies between project variables
5. Confidence intervals are calculated for completion dates at P10, P50, P80, and P90 levels

The simulation automatically identifies risk factors through pattern recognition in the simulation results, applying clustering algorithms to identify emergent risks not specified in the initial model.

## Database Schema

The API is backed by a sophisticated time-series database with the following schema:

### EVM Metrics Table
```sql
CREATE TABLE evm_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    pv REAL,
    ev REAL,
    ac REAL,
    sv REAL,
    cv REAL,
    spi REAL,
    cpi REAL,
    etc REAL,
    eac REAL,
    tcpi REAL,
    created_at TEXT NOT NULL
)
```

### Forecasts Table
```sql
CREATE TABLE forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    forecast_type TEXT NOT NULL,
    forecast_data TEXT NOT NULL,
    model_params TEXT,
    accuracy REAL,
    confidence_interval REAL,
    rmse REAL,
    mae REAL,
    created_at TEXT NOT NULL
)
```

### Sensitivity Analyses Table
```sql
CREATE TABLE sensitivity_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    parameters TEXT NOT NULL,
    results TEXT NOT NULL,
    key_findings TEXT,
    created_at TEXT NOT NULL
)
```

### Monte Carlo Simulations Table
```sql
CREATE TABLE monte_carlo_simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    simulation_runs INTEGER NOT NULL,
    distribution_data TEXT NOT NULL,
    p10_completion TEXT,
    p50_completion TEXT,
    p80_completion TEXT,
    p90_completion TEXT,
    risk_factors TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL
)
```

### Risk Factors Table
```sql
CREATE TABLE risk_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    risk_name TEXT NOT NULL,
    impact TEXT NOT NULL,
    probability REAL,
    confidence REAL,
    detection_method TEXT,
    mitigation_strategy TEXT,
    status TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
)
```

## Error Handling

API errors follow standard HTTP status codes with JSON error responses:

```json
{
  "error": "Error message details"
}
```

Common error codes:
- 400: Bad Request - Invalid request parameters
- 404: Not Found - Resource not found
- 500: Internal Server Error - Server-side error during processing

## Rate Limiting

Production implementations should implement appropriate rate limiting based on computational intensity of each endpoint:
- `/forecast`: 10 requests per minute
- `/sensitivity`: 5 requests per minute
- `/monte-carlo`: 2 requests per minute

## Versioning

API versioning is included in the URL path (/api/v1/) to ensure backward compatibility as new features are added.
