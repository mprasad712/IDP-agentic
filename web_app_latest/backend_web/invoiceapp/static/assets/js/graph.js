var headerHeight = 0;
var paddingArea = 5;
var graphPaddingArea = 30;
var graphTablePaddingArea = 10;
var divAreaHeight = ($( window ).height()- headerHeight );

var jsonData =  [ {
	  "label" : "105",
	  "value" : "2"
	}, {
	  "label" : "106",
	  "value" : "1"
	}, {
	  "label" : "215",
	  "value" : "1"
	}, {
	  "label" : "852",
	  "value" : "1"
	}, {
	  "label" : "921",
	  "value" : "3"
	} ]

var jsonData1 =  [ {
	  "label" : "20",
	  "value" : "2"
	}, {
	  "label" : "30",
	  "value" : "1"
	}, {
	  "label" : "40",
	  "value" : "1"
	}, {
	  "label" : "50",
	  "value" : "1"
	}, {
	  "label" : "60",
	  "value" : "3"
	} ]


/*$(document).ready(function(){
	var graphdiv=document.getElementById('divGraphReportContainer');
	graphdiv.style.width = '100%';
	graphdiv.style.height = '250px';
	graphdiv.style.float='left';
});*/


/*$(document).ready(function(){
	var graphdiv=document.getElementById('divSecondGraphReportContainer');
	graphdiv.style.width = '100%';
	graphdiv.style.height = '250px';
	graphdiv.style.float='left';
});*/

function generateGraphReport(inputXML, divId) {
	var divHeight = $( window ).height();
	divHeight = divHeight - headerHeight - paddingArea - graphPaddingArea;
	var revenueChart = new FusionCharts({
		"type" : "column2d",
		"renderAt" : divId,
		"width" : "100%",
		"height" : "200px",
		"dataFormat" : "json",
	    "dataSource": {
	      "chart": {
	    	  "axisLineAlpha": "25", 
	    	  "bgColor": "#ffffff", 
	    	  "caption": "Clearance Module", 
	    	  "captionFontSize": "14", 
	    	  "divLineAlpha": "10", 
	    	  "numberPrefix": "", 
	    	  "paletteColors": "#ff8080", 
	    	  "plotBorderAlpha": "10", 
	    	  "plotFillAlpha": "50", 
	    	  "showAlternateHGridColor": "0", 
	    	  "showBorder": "0", 
	    	  "showCanvasBorder": "0", 
	    	  "showValues": "1", 
	    	  "showXAxisLine": "1", 
	    	  "toolTipBgAlpha": "80", 
	    	  "toolTipBgColor": "#000000", 
	    	  "toolTipBorderRadius": "2", 
	    	  "toolTipBorderThickness": "0", 
	    	  "toolTipColor": "#ffffff", 
	    	  "toolTipPadding": "5", 
	    	  "usePlotGradientColor": "0", 
	    	  "xAxisName": "Client Code", 
	    	  "yAxisName": "No. of Cheques" 
	    	  } ,
	          "data": jsonData
	        }
	    });
	revenueChart.render();
}


function generateSecondGraphReport(inputXML, divId) {
	var divHeight = $( window ).height();
	divHeight = divHeight - headerHeight - paddingArea - graphPaddingArea;
	var revenueChart = new FusionCharts({
		"type" : "line",
		"renderAt" : divId,
		"width" : "100%",
		"height" : "200px",
		"dataFormat" : "json",
	    "dataSource": {
	      "chart": {
	    	  "axisLineAlpha": "25", 
	    	  "bgColor": "#ffffff", 
	    	  "caption": "Number Of Users", 
	    	  "captionFontSize": "14", 
	    	  "divLineAlpha": "10", 
	    	  "numberPrefix": "", 
	    	  "paletteColors": "#0075c2", 
	    	  "plotBorderAlpha": "10", 
	    	  "plotFillAlpha": "50", 
	    	  "showAlternateHGridColor": "0", 
	    	  "showBorder": "0", 
	    	  "showCanvasBorder": "0", 
	    	  "showValues": "1", 
	    	  "showXAxisLine": "1", 
	    	  "toolTipBgAlpha": "80", 
	    	  "toolTipBgColor": "#000000", 
	    	  "toolTipBorderRadius": "2", 
	    	  "toolTipBorderThickness": "0", 
	    	  "toolTipColor": "#ffffff", 
	    	  "toolTipPadding": "5", 
	    	  "usePlotGradientColor": "0", 
	    	  "xAxisName": "Client Code", 
	    	  "yAxisName": "No. of Cheques" 
	    	  } ,
	          "data": jsonData
	        }
	    });
	revenueChart.render();
}


function generateThirdGraphReport(inputXML, divId) {
	var divHeight = $( window ).height();
	divHeight = divHeight - headerHeight - paddingArea - graphPaddingArea;
	var revenueChart = new FusionCharts({
		"type" : "pie3d",
		"renderAt" : divId,
		"width" : "100%",
		"height" : "200px",
		"dataFormat" : "json",
	    "dataSource": {
	      "chart": {
	    	  "bgColor": "#ffffff", 
	    	  "caption": "Split of Visitors by Age Group", 
	    	  "captionFontSize": "14", 
	    	  "decimals": "1", 
	    	  "enableSmartLabels": "0", 
	    	  "legendBgColor": "#ffffff", 
	    	  "legendBorderAlpha": "0", 
	    	  "legendItemFontColor": "#666666", 
	    	  "legendItemFontSize": "10", 
	    	  "legendShadow": "0", 
	    	  "paletteColors": "#0075c2,#1aaf5d,#f2c500,#f45b00,#8e0000", 
	    	  "showBorder": "0", 
	    	  "showHoverEffect": "1", 
	    	  "showLegend": "1", 
	    	  "showPercentInTooltip": "0", 
	    	  "showPercentValues": "1", 
	    	  "showShadow": "0", 
	    	  "startingAngle": "0", 
	    	  "subCaption": "Last Month", 
	    	  "subcaptionFontBold": "0", 
	    	  "subcaptionFontSize": "14", 
	    	  "toolTipBgAlpha": "80", 
	    	  "toolTipBgColor": "#000000", 
	    	  "toolTipBorderRadius": "2", 
	    	  "toolTipBorderThickness": "0", 
	    	  "toolTipColor": "#ffffff", 
	    	  "toolTipPadding": "5", 
	    	  "use3DLighting": "0", 
	    	  "useDataPlotColorForLabels": "1" 
	    	  } ,
	          "data": jsonData1
	        }
	    });
	revenueChart.render();
}

