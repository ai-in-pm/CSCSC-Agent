/**
 * Primavera P6 Integration for CSCSC AI Agent
 * 
 * This module provides JavaScript functionality to visualize and interact with 
 * Primavera P6 project data within the CSCSC AI Agent dashboard.
 */

// Initialize the Primavera visualization module
const PrimaveraVisualization = (function() {
    // Private variables
    let projectData = null;
    let currentProjectId = null;
    let charts = {};
    
    // DOM Element references
    const domElements = {
        projectSelector: null,
        projectInfoPanel: null,
        ganttContainer: null,
        resourceContainer: null,
        progressContainer: null,
        loadingSpinner: null,
        errorMessage: null,
        queryInput: null,
        queryButton: null,
        queryResult: null
    };
    
    // Initialize module
    function init(config) {
        console.log('Initializing Primavera Visualization');
        
        // Store DOM element references
        domElements.projectSelector = document.getElementById(config.projectSelectorId || 'primavera-project-selector');
        domElements.projectInfoPanel = document.getElementById(config.projectInfoPanelId || 'primavera-project-info');
        domElements.ganttContainer = document.getElementById(config.ganttContainerId || 'primavera-gantt-chart');
        domElements.resourceContainer = document.getElementById(config.resourceContainerId || 'primavera-resource-chart');
        domElements.progressContainer = document.getElementById(config.progressContainerId || 'primavera-progress-chart');
        domElements.loadingSpinner = document.getElementById(config.loadingSpinnerId || 'primavera-loading');
        domElements.errorMessage = document.getElementById(config.errorMessageId || 'primavera-error');
        domElements.queryInput = document.getElementById(config.queryInputId || 'primavera-query-input');
        domElements.queryButton = document.getElementById(config.queryButtonId || 'primavera-query-button');
        domElements.queryResult = document.getElementById(config.queryResultId || 'primavera-query-result');
        
        // Set up event handlers
        setupEventHandlers();
        
        // Load project data initially
        loadProjectData();
    }
    
    // Set up event handlers for user interaction
    function setupEventHandlers() {
        // Project selection change handler
        if (domElements.projectSelector) {
            domElements.projectSelector.addEventListener('change', function(e) {
                currentProjectId = e.target.value;
                renderProjectData(currentProjectId);
            });
        }
        
        // Query button click handler
        if (domElements.queryButton && domElements.queryInput) {
            domElements.queryButton.addEventListener('click', function() {
                const query = domElements.queryInput.value.trim();
                if (query) {
                    queryPrimaveraData(query);
                }
            });
            
            // Also trigger on Enter key
            domElements.queryInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const query = domElements.queryInput.value.trim();
                    if (query) {
                        queryPrimaveraData(query);
                    }
                }
            });
        }
    }
    
    // Load project data from API
    function loadProjectData() {
        showLoading(true);
        showError(null);
        
        fetch('/api/v1/primavera/projects')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                projectData = data;
                populateProjectSelector(data.projects);
                showLoading(false);
                
                // If projects exist, render the first one
                if (data.projects && data.projects.length > 0) {
                    currentProjectId = data.projects[0].id;
                    renderProjectData(currentProjectId);
                }
            })
            .catch(error => {
                console.error('Error loading Primavera data:', error);
                showError('Failed to load Primavera project data. ' + error.message);
                showLoading(false);
            });
    }
    
    // Populate project selector dropdown
    function populateProjectSelector(projects) {
        if (!domElements.projectSelector || !projects || !projects.length) {
            return;
        }
        
        // Clear existing options
        domElements.projectSelector.innerHTML = '';
        
        // Add options for each project
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            domElements.projectSelector.appendChild(option);
        });
    }
    
    // Render project data for the selected project
    function renderProjectData(projectId) {
        if (!projectData || !projectId) {
            return;
        }
        
        showLoading(true);
        
        // Find selected project
        const selectedProject = projectData.projects.find(p => p.id === projectId);
        
        if (!selectedProject) {
            showError('Project not found');
            showLoading(false);
            return;
        }
        
        // Render project info
        renderProjectInfo(selectedProject);
        
        // Get detailed data for selected project
        fetch(`/api/v1/primavera/projects/${projectId}/details`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(projectDetails => {
                // Render visualizations
                renderGanttChart(projectDetails.gantt_data);
                renderResourceChart(projectDetails.resource_data);
                renderProgressChart(projectDetails.progress_data);
                showLoading(false);
            })
            .catch(error => {
                console.error('Error loading project details:', error);
                showError('Failed to load project details. ' + error.message);
                showLoading(false);
            });
    }
    
    // Render project info panel
    function renderProjectInfo(project) {
        if (!domElements.projectInfoPanel) {
            return;
        }
        
        // Format dates for display
        const startDate = project.start_date ? new Date(project.start_date).toLocaleDateString() : 'Not set';
        const endDate = project.end_date ? new Date(project.end_date).toLocaleDateString() : 'Not set';
        
        // Create project info HTML
        const infoHtml = `
            <h3>${project.name}</h3>
            <div class="info-grid">
                <div class="info-label">ID:</div>
                <div class="info-value">${project.id}</div>
                
                <div class="info-label">Start Date:</div>
                <div class="info-value">${startDate}</div>
                
                <div class="info-label">End Date:</div>
                <div class="info-value">${endDate}</div>
                
                <div class="info-label">Progress:</div>
                <div class="info-value">
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${project.progress}%"></div>
                    </div>
                    <span>${project.progress.toFixed(1)}%</span>
                </div>
            </div>
        `;
        
        domElements.projectInfoPanel.innerHTML = infoHtml;
    }
    
    // Render Gantt chart visualization
    function renderGanttChart(ganttData) {
        if (!domElements.ganttContainer) {
            return;
        }
        
        // Clear existing chart
        domElements.ganttContainer.innerHTML = '';
        
        if (!ganttData || !ganttData.tasks || !ganttData.tasks.length) {
            domElements.ganttContainer.innerHTML = '<div class="no-data-message">No activity data available</div>';
            return;
        }
        
        // Create table for Gantt chart
        const tableHtml = `
            <table class="gantt-chart">
                <thead>
                    <tr>
                        <th>Activity</th>
                        <th>Timeline</th>
                    </tr>
                </thead>
                <tbody>
                    ${ganttData.tasks.map(task => {
                        const startDate = new Date(task.start);
                        const endDate = new Date(task.end);
                        const duration = (endDate - startDate) / (1000 * 60 * 60 * 24); // in days
                        
                        // Calculate position and width based on date range
                        const projectStartDate = new Date(ganttData.tasks[0].start);
                        const lastTask = ganttData.tasks[ganttData.tasks.length - 1];
                        const projectEndDate = new Date(lastTask.end);
                        const projectDuration = (projectEndDate - projectStartDate) / (1000 * 60 * 60 * 24);
                        
                        const leftPos = ((startDate - projectStartDate) / (1000 * 60 * 60 * 24)) / projectDuration * 100;
                        const widthPercent = duration / projectDuration * 100;
                        
                        return `
                            <tr>
                                <td class="gantt-task-name">${task.name}</td>
                                <td class="gantt-task-timeline">
                                    <div class="gantt-timeline-container">
                                        <div class="gantt-task-bar" style="left: ${leftPos}%; width: ${widthPercent}%;">
                                            <div class="gantt-task-progress" style="width: ${task.progress}%;"></div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
        
        domElements.ganttContainer.innerHTML = tableHtml;
    }
    
    // Render Resource chart
    function renderResourceChart(resourceData) {
        if (!domElements.resourceContainer) {
            return;
        }
        
        // Clear existing chart
        if (charts.resourceChart) {
            charts.resourceChart.destroy();
            charts.resourceChart = null;
        }
        
        if (!resourceData || !resourceData.resources || !resourceData.resources.length) {
            domElements.resourceContainer.innerHTML = '<div class="no-data-message">No resource data available</div>';
            return;
        }
        
        // Create canvas for chart
        domElements.resourceContainer.innerHTML = '<canvas id="resource-chart-canvas"></canvas>';
        const canvas = document.getElementById('resource-chart-canvas');
        const ctx = canvas.getContext('2d');
        
        // Prepare data for chart
        const labels = resourceData.resources.map(r => r.name);
        const plannedData = resourceData.resources.map(r => r.planned_units);
        const actualData = resourceData.resources.map(r => r.actual_units);
        
        // Create chart
        charts.resourceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Planned Units',
                        data: plannedData,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Actual Units',
                        data: actualData,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Units'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Resources'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Resource Allocation'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw.toFixed(1)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Render Progress S-curve chart
    function renderProgressChart(progressData) {
        if (!domElements.progressContainer) {
            return;
        }
        
        // Clear existing chart
        if (charts.progressChart) {
            charts.progressChart.destroy();
            charts.progressChart = null;
        }
        
        if (!progressData || !progressData.progress_curve || !progressData.progress_curve.length) {
            domElements.progressContainer.innerHTML = '<div class="no-data-message">No progress data available</div>';
            return;
        }
        
        // Create canvas for chart
        domElements.progressContainer.innerHTML = '<canvas id="progress-chart-canvas"></canvas>';
        const canvas = document.getElementById('progress-chart-canvas');
        const ctx = canvas.getContext('2d');
        
        // Prepare data for chart
        const labels = progressData.progress_curve.map(p => p.date);
        const plannedData = progressData.progress_curve.map(p => p.planned);
        
        // Create datasets (actual data might not be available for future dates)
        const datasets = [
            {
                label: 'Planned Progress',
                data: plannedData,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }
        ];
        
        // Add actual data if available
        const actualData = progressData.progress_curve
            .map(p => p.is_actual ? p.actual : null);
            
        if (actualData.some(v => v !== null)) {
            datasets.push({
                label: 'Actual Progress',
                data: actualData,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }
        
        // Find current date index
        const currentDateIndex = progressData.progress_curve.findIndex(p => !p.is_actual) - 1;
        
        // Create chart
        charts.progressChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Progress (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Project Progress S-Curve'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                xMin: currentDateIndex,
                                xMax: currentDateIndex,
                                borderColor: 'rgba(0, 0, 0, 0.5)',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    display: true,
                                    content: 'Today',
                                    position: 'start'
                                }
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Query Primavera data with natural language
    function queryPrimaveraData(query) {
        if (!domElements.queryResult) {
            return;
        }
        
        showLoading(true);
        domElements.queryResult.innerHTML = '';
        
        // Call the query API
        fetch('/api/v1/primavera/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                renderQueryResult(data);
                showLoading(false);
            })
            .catch(error => {
                console.error('Error querying Primavera data:', error);
                domElements.queryResult.innerHTML = `<div class="error-message">Query error: ${error.message}</div>`;
                showLoading(false);
            });
    }
    
    // Render query result
    function renderQueryResult(data) {
        if (!domElements.queryResult) {
            return;
        }
        
        if (!data || !data.result) {
            domElements.queryResult.innerHTML = '<div class="no-data-message">No results found</div>';
            return;
        }
        
        // Check if result is text or data
        if (typeof data.result === 'string') {
            // Text result
            domElements.queryResult.innerHTML = `<div class="query-text-result">${data.result}</div>`;
        } else if (Array.isArray(data.result)) {
            // Table result
            if (data.result.length === 0) {
                domElements.queryResult.innerHTML = '<div class="no-data-message">No results found</div>';
                return;
            }
            
            // Create table from result
            const columns = Object.keys(data.result[0]);
            const tableHtml = `
                <table class="query-result-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.result.map(row => `
                            <tr>
                                ${columns.map(col => `<td>${row[col] !== null ? row[col] : ''}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            domElements.queryResult.innerHTML = tableHtml;
        } else if (typeof data.result === 'object' && data.visualization) {
            // Result with visualization
            domElements.queryResult.innerHTML = `<div class="query-text-result">${data.text_result}</div>`;
            
            // Create canvas for visualization
            const canvasId = 'query-result-chart';
            const canvasHtml = `<canvas id="${canvasId}"></canvas>`;
            domElements.queryResult.innerHTML += canvasHtml;
            
            // Create chart based on visualization type
            const canvas = document.getElementById(canvasId);
            createVisualization(canvas, data.visualization);
        } else {
            // Generic object result
            domElements.queryResult.innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
        }
    }
    
    // Create visualization for query result
    function createVisualization(canvas, visualization) {
        if (!canvas || !visualization || !visualization.type) {
            return;
        }
        
        const ctx = canvas.getContext('2d');
        let chart;
        
        switch (visualization.type) {
            case 'bar':
                chart = new Chart(ctx, {
                    type: 'bar',
                    data: visualization.data,
                    options: visualization.options || {}
                });
                break;
                
            case 'line':
                chart = new Chart(ctx, {
                    type: 'line',
                    data: visualization.data,
                    options: visualization.options || {}
                });
                break;
                
            case 'pie':
                chart = new Chart(ctx, {
                    type: 'pie',
                    data: visualization.data,
                    options: visualization.options || {}
                });
                break;
                
            default:
                console.error('Unsupported visualization type:', visualization.type);
        }
    }
    
    // Show/hide loading spinner
    function showLoading(show) {
        if (domElements.loadingSpinner) {
            domElements.loadingSpinner.style.display = show ? 'block' : 'none';
        }
    }
    
    // Show/clear error message
    function showError(message) {
        if (domElements.errorMessage) {
            if (message) {
                domElements.errorMessage.textContent = message;
                domElements.errorMessage.style.display = 'block';
            } else {
                domElements.errorMessage.textContent = '';
                domElements.errorMessage.style.display = 'none';
            }
        }
    }
    
    // Public API
    return {
        init: init,
        refresh: loadProjectData,
        renderProject: renderProjectData,
        query: queryPrimaveraData
    };
})();
