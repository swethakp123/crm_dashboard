/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from  "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { onMounted } from "@odoo/owl";
import { useRef } from "@odoo/owl";
import { onWillStart } from "@odoo/owl";



const actionRegistry = registry.category("actions");
class CrmDashboard extends Component {
    setup() {
        super.setup()
        this.actionService = useService("action");
        this.orm = useService('orm')

        this.inputStartLead = useRef("inputStartLead");
        this.inputStartOpportunity = useRef("inputStartOpportunity");
        this.inputStartRevenue = useRef("inputStartRevenue");
        this.inputStartWinRatio= useRef("inputStartWinRatio");
        this.inputStartTotalRevenue = useRef("inputStartTotalRevenue");
        this.inputStartLeadsMonth = useRef("inputStartLeadsMonth");
        onMounted(async () => {await loadJS(["/web/static/lib/Chart/Chart.js"]);
                              await this._fetchData('year');

      });
    }

    //By clicking on lead tile it will redirect to list view of leads
    async _onClickLead() {
    const filterValue = $('#timeIntervalDropdown').find(":selected").val();
        const result = await this.orm.call("crm.lead","get_tiles_data", [filterValue], {});
        const leadCount = result.total_leads;

        if (leadCount > 0) {
            const leads = await this.orm.call("crm.lead", "search", [[]]);
            const leadIds = leads.slice(0, leadCount);

            const action = await this.actionService.doAction({
                name: _t('My Leads'),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                views: [[false, "list"]],
                domain: [['id', 'in', leadIds]],
                target: 'current',
                context: {
                    active_ids: leadIds,
                },
            });
        } else {
            console.log("No leads to show.");
        }
    }

    //By clicking on Opportunity tile it will redirect to list view of Opportunity
    async _onClickOpportunity() {
    const filterValue = $('#timeIntervalDropdown').find(":selected").val();
    const result = await this.orm.call("crm.lead","get_tiles_data", [filterValue], {});
    const opportunityCount = result.total_opportunity;


    if (opportunityCount > 0) {
        const leads = await this.orm.call("crm.lead", "search", [[]]);
        const oppIds = leads.slice(0, opportunityCount);

        const action = await this.actionService.doAction({
            name: _t('My Opportunity'),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            views: [[false, "list"]],
            domain: [['id', 'in', oppIds]],
            target: 'current',
            context: {
                active_ids: oppIds,
            },
        });
    } else {
        console.log("No Opportunity to show.");
    }
    }

    // using orm call to fetch data based on timeinterval
    async _fetchData(time_interval) {
        var self = this;
        const result = await this.orm.call("crm.lead","get_tiles_data", [time_interval], {});
        console.log('result111',result)
        $('#inputStartLead').empty();
        $('#inputStartOpportunity').empty();
        $('#revenue').empty();
        $('#win_ratio').empty();
        $('#total_revenue').empty();

        this.inputStartLead.el.append(result.total_leads);
        this.inputStartOpportunity.el.append(result.total_opportunity);
        this.inputStartRevenue.el.append(result.currency + result.expected_revenue);
        this.inputStartWinRatio.el.append(result.total_win_ratio);
        this.inputStartTotalRevenue.el.append(result.currency + result.total_revenue );
        if(this.chartpie){
            this.chartpie.destroy()
        }
        const leadByCampaignData = result.lead_by_campaign.map(r => r.lead_count);
        const leadByCampaignLabels = result.lead_by_campaign.map(r => r.campaign_name);
        self.chartpie = new Chart("chartpie", {
                type: 'pie',
        data: {
            labels: leadByCampaignLabels,
            datasets: [{
                data: leadByCampaignData
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
            }
        });
        //If it already exist Chart then destroy it
        if(this.chartPieMedium){
            this.chartPieMedium.destroy()
        }
        //Pie Chart View for Leads
        const leadByMediumData = result.lead_by_medium.map(r => r.lead_count);
        const leadByMediumLabels = result.lead_by_medium.map(r => r.medium_name);
        console.log('leadByMediumLabels', leadByMediumLabels)
        self.chartPieMedium = new Chart("chartPieMedium", {
                type: 'pie',
        data: {
            labels: leadByMediumLabels,
            datasets: [{
                data: leadByMediumData
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
            }
        });

        if(this.chartActivityLead){
            this.chartActivityLead.destroy()
        }
        const activityData = result.activity_data;
        const activityLabels = activityData.map(activity => activity.activity_type);
        const activityCounts = activityData.map(activity => activity.count);
        self.chartActivityLead = new Chart("chartActivityLead", {
                type: 'pie',
        data: {
            labels: activityLabels,
            datasets: [{
                data: activityCounts
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
            }
        });
        if(this.chartbar){
            this.chartbar.destroy()
        }
        self.chartbar = new Chart("chartbar", {
            type: "bar",
            data: {
            labels: ['Lost Leads','Lost Opportunity'],
                datasets: [{
                    label:['Count'],
                    backgroundColor: "MediumBlue",
                    data: [result.lost_leadss,result.lost_opportunities]
                }]
            },
            options: {}
        });
        if(this.chartLine){
            this.chartLine.destroy()
        }
        self.chartLine = new Chart("chartLine", {
            type: "line",
            data: {
            labels: ['Lost Leads','Lost Opportunity'],
                datasets: [{
                    label:['Count'],
                    pointBackgroundColor: "black",
                    data: [result.lost_opportunities, result.lost_leadss]
                }]
            },
            options: {}
        });

    };
};
CrmDashboard.template = "crm_dashboard.CrmDashboard";
actionRegistry.add("crm_dashboard_tag", CrmDashboard);