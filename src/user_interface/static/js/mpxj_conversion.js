/**
 * MPXJ Conversion UI for CSCSC AI Agent
 * 
 * This module provides JavaScript functionality for the MPXJ project file
 * conversion and analysis UI.
 */

// Initialize the file conversion module when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const MPXJConverter = {
        // Variables to track state
        currentFile: null,
        supportedFormats: null,
        charts: {},

        // DOM element references
        elements: {
            // File upload elements
            dropZone: document.getElementById('dropZone'),
            fileInput: document.getElementById('fileInput'),
            browseButton: document.getElementById('browseButton'),
            progressContainer: document.querySelector('.progress-container'),
            progressBar: document.querySelector('.progress-bar'),
            uploadStatus: document.getElementById('uploadStatus'),
            
            // File info elements
            fileInfoSection: document.getElementById('fileInfoSection'),
            fileName: document.getElementById('fileName'),
            fileFormat: document.getElementById('fileFormat'),
            fileSize: document.getElementById('fileSize'),
            
            // Action elements
            outputFormat: document.getElementById('outputFormat'),
            convertButton: document.getElementById('convertButton'),
            analyzeButton: document.getElementById('analyzeButton'),
            importButton: document.getElementById('importButton'),
            deleteButton: document.getElementById('deleteButton'),
            
            // Analysis options
            extractStats: document.getElementById('extractStats'),
            extractCriticalPath: document.getElementById('extractCriticalPath'),
            extractTasks: document.getElementById('extractTasks'),
            extractResources: document.getElementById('extractResources'),
            extractAssignments: document.getElementById('extractAssignments'),
            
            // Analysis results
            analysisSection: document.getElementById('analysisSection'),
            statisticsContainer: document.getElementById('statisticsContainer'),
            statisticsData: document.getElementById('statisticsData'),
            criticalPathContainer: document.getElementById('criticalPathContainer'),
            criticalPathData: document.getElementById('criticalPathData'),
            tablesContainer: document.getElementById('tablesContainer'),
            dataTabs: document.getElementById('dataTabs'),
            dataTabsContent: document.getElementById('dataTabsContent'),
            collapseAnalysisButton: document.getElementById('collapseAnalysisButton'),
            
            // Chart canvases
            taskDistributionChart: document.getElementById('taskDistributionChart'),
            resourceAllocationChart: document.getElementById('resourceAllocationChart')
        },

        /**
         * Initialize the conversion UI
         */
        init: function() {
            console.log('Initializing MPXJ Conversion UI');
            
            // Load supported formats
            this.loadSupportedFormats();
            
            // Set up event handlers
            this.setupEventHandlers();
        },

        /**
         * Load supported file formats from the API
         */
        loadSupportedFormats: function() {
            fetch('/api/v1/mpxj/formats')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.supportedFormats = data;
                    this.populateOutputFormats(data.write_formats);
                })
                .catch(error => {
                    console.error('Error loading supported formats:', error);
                    this.showError('Failed to load supported file formats. ' + error.message);
                });
        },

        /**
         * Populate the output format dropdown
         */
        populateOutputFormats: function(formats) {
            const select = this.elements.outputFormat;
            
            // Clear existing options
            select.innerHTML = '';
            
            // Add options for each format
            formats.forEach(format => {
                const option = document.createElement('option');
                option.value = format.extension;
                option.textContent = format.description;
                select.appendChild(option);
            });
        },

        /**
         * Set up event handlers for user interaction
         */
        setupEventHandlers: function() {
            // File upload handlers
            this.elements.dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.elements.dropZone.classList.add('active');
            });
            
            this.elements.dropZone.addEventListener('dragleave', () => {
                this.elements.dropZone.classList.remove('active');
            });
            
            this.elements.dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.elements.dropZone.classList.remove('active');
                
                if (e.dataTransfer.files.length > 0) {
                    this.handleFileUpload(e.dataTransfer.files[0]);
                }
            });
            
            this.elements.browseButton.addEventListener('click', () => {
                this.elements.fileInput.click();
            });
            
            this.elements.fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
            
            // Action button handlers
            this.elements.convertButton.addEventListener('click', () => {
                this.convertFile();
            });
            
            this.elements.analyzeButton.addEventListener('click', () => {
                this.analyzeFile();
            });
            
            this.elements.importButton.addEventListener('click', () => {
                this.importToDatabase();
            });
            
            this.elements.deleteButton.addEventListener('click', () => {
                this.deleteFile();
            });
            
            // Collapse button for analysis results
            this.elements.collapseAnalysisButton.addEventListener('click', () => {
                const content = document.getElementById('analysisContent');
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    this.elements.collapseAnalysisButton.innerHTML = '<i class="bi bi-chevron-up"></i>';
                } else {
                    content.style.display = 'none';
                    this.elements.collapseAnalysisButton.innerHTML = '<i class="bi bi-chevron-down"></i>';
                }
            });
        },

        /**
         * Handle file upload
         */
        handleFileUpload: function(file) {
            // Show progress indicator
            this.elements.progressContainer.style.display = 'block';
            this.elements.progressBar.style.width = '0%';
            this.elements.uploadStatus.textContent = 'Uploading...';
            
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Upload file
            fetch('/api/v1/mpxj/upload', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.currentFile = data;
                    this.showFileInfo(data);
                    this.elements.progressBar.style.width = '100%';
                    this.elements.uploadStatus.textContent = 'Upload complete!';
                    
                    // Hide progress after a delay
                    setTimeout(() => {
                        this.elements.progressContainer.style.display = 'none';
                    }, 1500);
                })
                .catch(error => {
                    console.error('Error uploading file:', error);
                    this.elements.progressContainer.style.display = 'none';
                    this.showError('Failed to upload file. ' + error.message);
                });
        },

        /**
         * Show file information
         */
        showFileInfo: function(fileInfo) {
            this.elements.fileInfoSection.style.display = 'block';
            this.elements.fileName.textContent = fileInfo.name;
            this.elements.fileFormat.textContent = fileInfo.format;
            this.elements.fileSize.textContent = this.formatFileSize(fileInfo.size);
        },

        /**
         * Format file size for display
         */
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        /**
         * Convert file to selected format
         */
        convertFile: function() {
            if (!this.currentFile) {
                this.showError('No file selected');
                return;
            }
            
            const outputFormat = this.elements.outputFormat.value;
            
            // Create fetch request
            fetch(`/api/v1/mpxj/convert/${this.currentFile.name}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    output_format: outputFormat
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.blob();
                })
                .then(blob => {
                    // Create download link
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = this.currentFile.name.replace(/\.[^\.]+$/, outputFormat);
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    this.showSuccess('File converted successfully!');
                })
                .catch(error => {
                    console.error('Error converting file:', error);
                    this.showError('Failed to convert file. ' + error.message);
                });
        },

        /**
         * Analyze file and display results
         */
        analyzeFile: function() {
            if (!this.currentFile) {
                this.showError('No file selected');
                return;
            }
            
            // Get analysis options
            const options = {
                extract_statistics: this.elements.extractStats.checked,
                extract_critical_path: this.elements.extractCriticalPath.checked,
                extract_tables: []
            };
            
            // Add selected tables
            if (this.elements.extractTasks.checked) options.extract_tables.push('tasks');
            if (this.elements.extractResources.checked) options.extract_tables.push('resources');
            if (this.elements.extractAssignments.checked) options.extract_tables.push('assignments');
            
            // Create fetch request
            fetch(`/api/v1/mpxj/analyze/${this.currentFile.name}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.displayAnalysisResults(data);
                })
                .catch(error => {
                    console.error('Error analyzing file:', error);
                    this.showError('Failed to analyze file. ' + error.message);
                });
        },

        /**
         * Display analysis results
         */
        displayAnalysisResults: function(data) {
            // Show analysis section
            this.elements.analysisSection.style.display = 'block';
            
            // Display statistics if available
            if (data.statistics) {
                this.elements.statisticsContainer.style.display = 'block';
                this.displayStatistics(data.statistics);
            } else {
                this.elements.statisticsContainer.style.display = 'none';
            }
            
            // Display critical path if available
            if (data.critical_path && data.critical_path.length > 0) {
                this.elements.criticalPathContainer.style.display = 'block';
                this.displayCriticalPath(data.critical_path);
            } else {
                this.elements.criticalPathContainer.style.display = 'none';
            }
            
            // Display tables if available
            if (data.tables && Object.keys(data.tables).length > 0) {
                this.elements.tablesContainer.style.display = 'block';
                this.displayTables(data.tables);
            } else {
                this.elements.tablesContainer.style.display = 'none';
            }
            
            // Create visualizations if data is available
            if (data.statistics || (data.tables && data.tables.tasks)) {
                this.createVisualizations(data);
            }
        },

        /**
         * Display project statistics
         */
        displayStatistics: function(stats) {
            // Create HTML for statistics
            const statsHtml = `
                <div class="col-md-4">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h6 class="card-title">Project Info</h6>
                            <p class="mb-1"><strong>Name:</strong> ${stats.name || 'N/A'}</p>
                            <p class="mb-1"><strong>Start Date:</strong> ${stats.start_date ? new Date(stats.start_date).toLocaleDateString() : 'N/A'}</p>
                            <p class="mb-1"><strong>Finish Date:</strong> ${stats.finish_date ? new Date(stats.finish_date).toLocaleDateString() : 'N/A'}</p>
                            <p class="mb-0"><strong>Status Date:</strong> ${stats.status_date ? new Date(stats.status_date).toLocaleDateString() : 'N/A'}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h6 class="card-title">Task Counts</h6>
                            <p class="mb-1"><strong>Total Tasks:</strong> ${stats.task_count}</p>
                            <p class="mb-1"><strong>Normal Tasks:</strong> ${stats.normal_task_count}</p>
                            <p class="mb-1"><strong>Milestones:</strong> ${stats.milestone_count}</p>
                            <p class="mb-0"><strong>Summary Tasks:</strong> ${stats.summary_task_count}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h6 class="card-title">Other Metrics</h6>
                            <p class="mb-1"><strong>Resources:</strong> ${stats.resource_count}</p>
                            <p class="mb-1"><strong>Duration (days):</strong> ${stats.total_duration_days.toFixed(1)}</p>
                            <p class="mb-0"><strong>Critical Path Length:</strong> ${stats.critical_path_length} tasks</p>
                        </div>
                    </div>
                </div>
            `;
            
            // Update the statistics container
            this.elements.statisticsData.innerHTML = statsHtml;
        },

        /**
         * Display critical path tasks
         */
        displayCriticalPath: function(criticalPath) {
            // Create HTML for critical path tasks
            let html = '';
            
            criticalPath.forEach(task => {
                html += `
                    <tr>
                        <td>${task.id}</td>
                        <td>${task.name}</td>
                        <td>${task.start ? new Date(task.start).toLocaleDateString() : 'N/A'}</td>
                        <td>${task.finish ? new Date(task.finish).toLocaleDateString() : 'N/A'}</td>
                        <td>${task.duration ? task.duration + ' ' + task.duration_units : 'N/A'}</td>
                    </tr>
                `;
            });
            
            // Update the critical path container
            this.elements.criticalPathData.innerHTML = html;
        },

        /**
         * Display data tables
         */
        displayTables: function(tables) {
            // Clear existing tabs and content
            this.elements.dataTabs.innerHTML = '';
            this.elements.dataTabsContent.innerHTML = '';
            
            // Create tabs for each table
            let firstTab = true;
            Object.keys(tables).forEach(tableName => {
                // Create tab
                const tabId = `${tableName}-tab`;
                const contentId = `${tableName}-content`;
                
                // Add tab link
                const tabLink = document.createElement('li');
                tabLink.className = 'nav-item';
                tabLink.innerHTML = `
                    <a class="nav-link ${firstTab ? 'active' : ''}" id="${tabId}" data-bs-toggle="tab" href="#${contentId}" role="tab">
                        ${this.capitalizeFirstLetter(tableName)}
                    </a>
                `;
                this.elements.dataTabs.appendChild(tabLink);
                
                // Add tab content
                const tabContent = document.createElement('div');
                tabContent.className = `tab-pane fade ${firstTab ? 'show active' : ''}`;
                tabContent.id = contentId;
                tabContent.role = 'tabpanel';
                
                // Create table HTML
                const tableData = tables[tableName];
                if (tableData && tableData.length > 0) {
                    // Get column headers from the first object
                    const columns = Object.keys(tableData[0]).filter(col => 
                        typeof tableData[0][col] !== 'object' || tableData[0][col] === null
                    );
                    
                    // Create table HTML
                    let tableHtml = `
                        <div class="table-responsive">
                            <table class="table table-striped table-sm">
                                <thead>
                                    <tr>
                                        ${columns.map(col => `<th>${this.formatColumnName(col)}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    // Add table rows
                    tableData.forEach(row => {
                        tableHtml += '<tr>';
                        columns.forEach(col => {
                            let value = row[col];
                            
                            // Format dates
                            if (value && typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/))
                                value = new Date(value).toLocaleString();
                                
                            tableHtml += `<td>${value !== null && value !== undefined ? value : ''}</td>`;
                        });
                        tableHtml += '</tr>';
                    });
                    
                    tableHtml += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    tabContent.innerHTML = tableHtml;
                } else {
                    tabContent.innerHTML = '<p>No data available</p>';
                }
                
                this.elements.dataTabsContent.appendChild(tabContent);
                firstTab = false;
            });
        },

        /**
         * Create visualizations based on analysis data
         */
        createVisualizations: function(data) {
            // Destroy existing charts
            Object.keys(this.charts).forEach(chartId => {
                if (this.charts[chartId]) {
                    this.charts[chartId].destroy();
                    this.charts[chartId] = null;
                }
            });
            
            // Create task distribution chart if statistics are available
            if (data.statistics) {
                const taskChartCtx = this.elements.taskDistributionChart.getContext('2d');
                this.charts.taskDistribution = new Chart(taskChartCtx, {
                    type: 'pie',
                    data: {
                        labels: ['Normal Tasks', 'Milestones', 'Summary Tasks'],
                        datasets: [{
                            data: [
                                data.statistics.normal_task_count,
                                data.statistics.milestone_count,
                                data.statistics.summary_task_count
                            ],
                            backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Task Distribution'
                            },
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
            
            // Create resource allocation chart if resource assignments are available
            if (data.tables && data.tables.assignments && data.tables.assignments.length > 0) {
                // Group assignments by resource
                const resourceMap = {};
                data.tables.assignments.forEach(assignment => {
                    const resourceName = assignment.resource_name;
                    if (!resourceMap[resourceName]) {
                        resourceMap[resourceName] = {
                            actualWork: 0,
                            remainingWork: 0
                        };
                    }
                    
                    resourceMap[resourceName].actualWork += assignment.actual_work || 0;
                    resourceMap[resourceName].remainingWork += assignment.remaining_work || 0;
                });
                
                // Prepare chart data
                const resourceNames = Object.keys(resourceMap);
                const actualWork = resourceNames.map(name => resourceMap[name].actualWork);
                const remainingWork = resourceNames.map(name => resourceMap[name].remainingWork);
                
                // Create chart
                const resourceChartCtx = this.elements.resourceAllocationChart.getContext('2d');
                this.charts.resourceAllocation = new Chart(resourceChartCtx, {
                    type: 'bar',
                    data: {
                        labels: resourceNames,
                        datasets: [
                            {
                                label: 'Actual Work',
                                data: actualWork,
                                backgroundColor: '#4e73df'
                            },
                            {
                                label: 'Remaining Work',
                                data: remainingWork,
                                backgroundColor: '#1cc88a'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Resource Allocation'
                            },
                            legend: {
                                position: 'bottom'
                            }
                        },
                        scales: {
                            x: {
                                stacked: true
                            },
                            y: {
                                stacked: true
                            }
                        }
                    }
                });
            }
        },

        /**
         * Import file to database
         */
        importToDatabase: function() {
            if (!this.currentFile) {
                this.showError('No file selected');
                return;
            }
            
            // Create fetch request
            fetch(`/api/v1/mpxj/import-to-database/${this.currentFile.name}`, {
                method: 'POST'
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.showSuccess('File imported to database successfully!');
                })
                .catch(error => {
                    console.error('Error importing to database:', error);
                    this.showError('Failed to import file to database. ' + error.message);
                });
        },

        /**
         * Delete uploaded file
         */
        deleteFile: function() {
            if (!this.currentFile) {
                this.showError('No file selected');
                return;
            }
            
            // Create fetch request
            fetch(`/api/v1/mpxj/files/${this.currentFile.name}`, {
                method: 'DELETE'
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Reset UI
                    this.currentFile = null;
                    this.elements.fileInfoSection.style.display = 'none';
                    this.elements.analysisSection.style.display = 'none';
                    
                    this.showSuccess('File deleted successfully!');
                })
                .catch(error => {
                    console.error('Error deleting file:', error);
                    this.showError('Failed to delete file. ' + error.message);
                });
        },

        /**
         * Show error message
         */
        showError: function(message) {
            // Create alert element
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Add to page
            document.querySelector('.container').prepend(alert);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        },

        /**
         * Show success message
         */
        showSuccess: function(message) {
            // Create alert element
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Add to page
            document.querySelector('.container').prepend(alert);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        },

        /**
         * Format column name for display
         */
        formatColumnName: function(name) {
            return name
                .replace(/_/g, ' ')
                .replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
        },

        /**
         * Capitalize first letter of a string
         */
        capitalizeFirstLetter: function(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }
    };

    // Initialize the module
    MPXJConverter.init();
});
