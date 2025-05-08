/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useRef, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";

const actionRegistry = registry.category("actions");

export class ChartjsSampleCRM extends Component {
    setup() {
        this.orm = useService('orm');
        this.action = useService("action");
        
        // State management
        this.searchQuery = useState({ value: "" });
        this.dateFilters = useState({
            startDate: this.getDefaultStartDate(),
            endDate: this.getDefaultEndDate()
        });
        this.stats = useState({
            totalCallCenterLeads: 0,
            totalReceptionLeads: 0,
            totalLeads: 0,
            totalCustomers: 0,
            callCenterData: [],
            receptionDataByStage: [],
            receptionData: [],
            leadDataBySource: [],
            leadDataByStage: [],
            customerDataByType: [],
            customerDataByCountry: []
        });

        // Chart references
        this.barChartRef = useRef("barChart");
        this.pieChartRef = useRef("pieChart");
        this.receptionBarChartRef = useRef("receptionBarChart");
        this.receptionPieChartRef = useRef("receptionPieChart");
        this.sourceChartRef = useRef("sourceChart");
        this.stageChartRef = useRef("stageChart");
        this.customerTypeChartRef = useRef("customerTypeChart");
        this.customerCountryChartRef = useRef("customerCountryChart");
        this.barChart = null;
        this.pieChart = null;
        this.receptionBarChart = null;
        this.receptionPieChart = null;
        this.sourceChart = null;
        this.stageChart = null;
        this.customerTypeChart = null;
        this.customerCountryChart = null;

        // Initial setup
        onWillStart(async () => {
            await loadJS(["/web/static/lib/Chart/Chart.js"]);
            await this.fetchStats();
        });

        onMounted(() => {
            this.renderCharts();
            this.setupChartResizeListeners();
        });

        onWillUnmount(() => {
            this.destroyAllCharts();
            window.removeEventListener('resize', this.handleResize);
        });

        // Method binding
        this.goToCRMPage = this.goToCRMPage.bind(this);
        this.goToCustomerPage = this.goToCustomerPage.bind(this);
        this.goToReceptionPage = this.goToReceptionPage.bind(this);
        this.fetchStats = this.fetchStats.bind(this);
        this.renderCharts = this.renderCharts.bind(this);
        this.destroyAllCharts = this.destroyAllCharts.bind(this);
        this.onSearchQueryChange = this.onSearchQueryChange.bind(this);
        this.applyDateFilter = this.applyDateFilter.bind(this);
        this.resetDateFilter = this.resetDateFilter.bind(this);
        this.handleResize = this.handleResize.bind(this);
    }

    destroyAllCharts() {
        if (this.barChart) this.barChart.destroy();
        if (this.pieChart) this.pieChart.destroy();
        if (this.receptionBarChart) this.receptionBarChart.destroy();
        if (this.receptionPieChart) this.receptionPieChart.destroy();
        if (this.sourceChart) this.sourceChart.destroy();
        if (this.stageChart) this.stageChart.destroy();
        if (this.customerTypeChart) this.customerTypeChart.destroy();
        if (this.customerCountryChart) this.customerCountryChart.destroy();
    }

    setupChartResizeListeners() {
        window.addEventListener('resize', this.handleResize);
    }

    handleResize() {
        clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    getDefaultStartDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 1);
        return date.toISOString().split('T')[0];
    }

    getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }

    async fetchStats() {
        try {
            // Get call center and reception source IDs
            const [callCenterSource, receptionSource] = await Promise.all([
                this.orm.search("utm.source", [['name', '=', '6033']], { limit: 1 }),
                this.orm.search("utm.source", [['name', '=', 'Walk In']], { limit: 1 })
            ]);
            
            // Build domains with date filters
            const leadDomain = [];
            const customerDomain = [];
            const callCenterDomain = callCenterSource.length ? [['source_id', '=', callCenterSource[0]]] : [];
            const receptionDomain = receptionSource.length ? [['source_id', '=', receptionSource[0]]] : [];

    
            const customersnew = await this.orm.searchRead("res.partner", [], ['name', 'is_company', 'customer_rank']);
            console.log("All partners:", customersnew);


            
            if (this.dateFilters.startDate) {
                leadDomain.push(['create_date', '>=', this.dateFilters.startDate]);
                customerDomain.push(['create_date', '>=', this.dateFilters.startDate]);
                if (callCenterSource.length) {
                    callCenterDomain.push(['create_date', '>=', this.dateFilters.startDate]);
                }
                if (receptionSource.length) {
                    receptionDomain.push(['create_date', '>=', this.dateFilters.startDate]);
                }
            }
            if (this.dateFilters.endDate) {
                leadDomain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
                customerDomain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
                if (callCenterSource.length) {
                    callCenterDomain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
                }
                if (receptionSource.length) {
                    receptionDomain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
                }
            }
            
            // Get counts and data
            const [
                totalCallCenterLeads, 
                totalReceptionLeads,
                totalLeads, 
                totalCustomers,
                callCenterData, 
                receptionDataByStage,
                receptionData,
                leadDataBySource, 
                leadDataByStage,
                customerDataByType,
                customerDataByCountry
            ] = await Promise.all([
                callCenterSource.length ? this.orm.searchCount("crm.lead", callCenterDomain) : 0,
                receptionSource.length ? this.orm.searchCount("crm.lead", receptionDomain) : 0,
                this.orm.searchCount("crm.lead", leadDomain),
                this.orm.searchCount("res.partner", [...customerDomain, ['customer_rank', '>', 0]]),
                callCenterSource.length ? this.orm.readGroup(
                    "crm.lead",
                    callCenterDomain,
                    ['stage_id'],
                    ['stage_id']
                ) : [],
                receptionSource.length ? this.orm.readGroup(
                    "crm.lead",
                    receptionDomain,
                    ['stage_id'],
                    ['stage_id']
                ) : [],
                receptionSource.length ? this.orm.readGroup(
                    "crm.reception",
                    [['create_date', '>=', this.dateFilters.startDate],
                     ['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']],
                    ['state'],
                    ['state']
                ) : [],
                this.orm.readGroup(
                    "crm.lead",
                    leadDomain,
                    ['source_id'],
                    ['source_id']
                ),
                this.orm.readGroup(
                    "crm.lead",
                    leadDomain,
                    ['stage_id'],
                    ['stage_id']
                ),
                this.orm.readGroup(
                    "res.partner",
                    [...customerDomain, ['customer_rank', '>', 0]],
                    ['is_company'],
                    ['is_company']
                ),
                this.orm.readGroup(
                    "res.partner",
                    [...customerDomain, ['customer_rank', '>', 0]],
                    ['country_id'],
                    ['country_id']
                )
            ]);

            // Log customer data for debugging
            console.log("Customer Data by Type:", customerDataByType);
            console.log("Customer Data by Country:", customerDataByCountry);

            this.stats.totalCallCenterLeads = totalCallCenterLeads;
            this.stats.totalReceptionLeads = totalReceptionLeads;
            this.stats.customersnew = customersnew.length;
            this.stats.totalLeads = totalLeads;
            this.stats.totalCustomers = totalCustomers;
            this.stats.callCenterData = callCenterData;
            this.stats.receptionDataByStage = receptionDataByStage;
            this.stats.receptionData = receptionData;
            this.stats.leadDataBySource = leadDataBySource;
            this.stats.leadDataByStage = leadDataByStage;
            this.stats.customerDataByType = customerDataByType;
            this.stats.customerDataByCountry = customerDataByCountry;
        } catch (error) {
            console.error("Error fetching stats:", error);
        }
    }

    renderCharts() {
        this.destroyAllCharts();

        // Call Center Charts
        if (this.stats.callCenterData.length) {
            const labels = this.stats.callCenterData.map(item => item.stage_id[1]);
            const data = this.stats.callCenterData.map(item => item.stage_id_count);
            const backgroundColors = labels.map((_, index) => getColor(index));

            // Bar Chart
            this.barChart = new Chart(this.barChartRef.el, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Call Center Leads by Stage',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });

            // Pie Chart
            this.pieChart = new Chart(this.pieChartRef.el, {
                type: "pie",
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        }

        // Reception Charts (same style as Call Center)
        if (this.stats.receptionDataByStage.length) {
            const labels = this.stats.receptionDataByStage.map(item => item.stage_id[1]);
            const data = this.stats.receptionDataByStage.map(item => item.stage_id_count);
            const backgroundColors = labels.map((_, index) => getColor(index + 5));

            // Bar Chart
            this.receptionBarChart = new Chart(this.receptionBarChartRef.el, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Reception Leads by Stage',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });

            // Pie Chart
            this.receptionPieChart = new Chart(this.receptionPieChartRef.el, {
                type: "pie",
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        }

        // All Leads Charts
        if (this.stats.leadDataBySource.length) {
            const sourceLabels = this.stats.leadDataBySource.map(item => item.source_id ? item.source_id[1] : 'Undefined');
            const sourceData = this.stats.leadDataBySource.map(item => item.source_id_count);
            const sourceColors = sourceLabels.map((_, index) => getColor(index + 10));

            this.sourceChart = new Chart(this.sourceChartRef.el, {
                type: "doughnut",
                data: {
                    labels: sourceLabels,
                    datasets: [{
                        data: sourceData,
                        backgroundColor: sourceColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        }

        if (this.stats.leadDataByStage.length) {
            const stageLabels = this.stats.leadDataByStage.map(item => item.stage_id[1]);
            const stageData = this.stats.leadDataByStage.map(item => item.stage_id_count);
            const stageColors = stageLabels.map((_, index) => getColor(index + 15));

            this.stageChart = new Chart(this.stageChartRef.el, {
                type: "bar",
                data: {
                    labels: stageLabels,
                    datasets: [{
                        label: 'All Leads by Stage',
                        data: stageData,
                        backgroundColor: stageColors,
                        borderColor: stageColors.map(color => color.replace('0.6', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });
        }

        // Customer Charts
        if (this.stats.customerDataByType.length) {
            const typeLabels = this.stats.customerDataByType.map(item => 
                item.is_company ? 'Company' : 'Individual'
            );
            const typeData = this.stats.customerDataByType.map(item => item.is_company_count);
            const typeColors = ['#3b82f6', '#10b981'];

            this.customerTypeChart = new Chart(this.customerTypeChartRef.el, {
                type: "pie",
                data: {
                    labels: typeLabels,
                    datasets: [{
                        data: typeData,
                        backgroundColor: typeColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        }

        if (this.stats.customerDataByCountry.length) {
            const countryLabels = this.stats.customerDataByCountry.map(item => 
                item.country_id ? item.country_id[1] : 'No Country'
            );
            const countryData = this.stats.customerDataByCountry.map(item => item.country_id_count);
            const countryColors = countryLabels.map((_, index) => getColor(index + 20));

            this.customerCountryChart = new Chart(this.customerCountryChartRef.el, {
                type: "pie",
                data: {
                    labels: countryLabels,
                    datasets: [{
                        data: countryData,
                        backgroundColor: countryColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        }
    }

    async applyDateFilter() {
        await this.fetchStats();
        this.renderCharts();
    }

    async resetDateFilter() {
        this.dateFilters.startDate = this.getDefaultStartDate();
        this.dateFilters.endDate = this.getDefaultEndDate();
        await this.fetchStats();
        this.renderCharts();
    }

    onSearchQueryChange(event) {
        this.searchQuery.value = event.target.value;
    }

    goToCRMPage(filter) {
        const domain = [];
        
        if (filter === 'callcenter') {
            domain.push(["source_id.name", "=", "6033"]);
        } else if (filter === 'reception') {
            domain.push(["source_id.name", "=", "Walk In"]);
        }
        
        if (this.dateFilters.startDate) {
            domain.push(['create_date', '>=', this.dateFilters.startDate]);
        }
        if (this.dateFilters.endDate) {
            domain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
        }

        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.lead",
            view_mode: "list",
            views: [[false, "list"]],
            target: "current",
            domain: domain,
        });
    }

    goToReceptionPage() {
        const domain = [];
        
        if (this.dateFilters.startDate) {
            domain.push(['create_date', '>=', this.dateFilters.startDate]);
        }
        if (this.dateFilters.endDate) {
            domain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
        }

        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.reception",
            view_mode: "list",
            views: [[false, "list"]],
            target: "current",
            domain: domain,
        });
    }

    // goToCustomerPage() {
    //     const domain = [['customer_rank', '>', 0]];
        
    //     if (this.dateFilters.startDate) {
    //         domain.push(['create_date', '>=', this.dateFilters.startDate]);
    //     }
    //     if (this.dateFilters.endDate) {
    //         domain.push(['create_date', '<=', this.dateFilters.endDate + ' 23:59:59']);
    //     }

    //     this.action.doAction({
    //         type: "ir.actions.act_window",
    //         res_model: "res.partner",
    //         view_mode: "list",
    //         views: [[false, "list"]],
    //         target: "current",
    //         domain: domain,
    //     });
    // }

    goToCustomerPage() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            view_mode: "list",
            views: [[false, "list"]],
            target: "current",
            domain: [['customer_rank', '>', 0]],  // Show all customers
        });
    }
    
}

ChartjsSampleCRM.template = "crm_dashboard.chartjs_sample_crm";
actionRegistry.add("chartjs_sample_crm", ChartjsSampleCRM);