$.get('/loadlogs', updateCallback);

update_time = 1000 * 60 * 60 * 24

Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

function poll(){
 $.get('/updatelogs', updateCallback);
}

graph_data = { 'label' : [], 'graph_data': []}


function updateCallback(data, textStatus){
  $('#time_div').html(data); // just replace a chunk of text with the new text
  $('#eth_price').html(data['value']);
  graph_data = data['line_data'];
  pie_data = data['pie_data']
  pie_drill_data = data['pie_data']
  renderGraph();
  renderPie();
  setTimeout(poll, update_time);
}

function renderGraph(){
    chart = new Highcharts.chart('container', {
        chart: {
            type: 'line'
        },

        title: {
            text: 'CBDefense Errors'
        },
        yAxis: {
            title: {
                text: 'Number of Errors'
            }
        },
        xAxis: {
                type: 'datetime'
            },
        plotOptions: {
            series: {
                dataLabels: {
        	        enabled: false
        	    },
        	    line: {
                    dataLabels: {
                        enabled: false
                    }
                }
            },

        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }

    });
    $.each(graph_data, function(name, data){
        chart.addSeries({
            name: name,
            data: data,
            visible: false,
        }, false)
    })
    chart.series[0].visible = true
    chart.redraw()
}

function renderPie(){
    chart = new Highcharts.chart('pie_container', {
        chart: {
            type: 'pie'
        },
        title: {
            text: 'Latest CBDefense Errors'
        },
        subtitle: {
            text: 'Click the slices to perform a query on them'
        },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true,
                    format: '{point.name}: {point.y}'
                },
                events: {
                    click: function (event) {
                        window.location.replace('/SearchError?search_string=' + event.point.drilldown);
                    }
                }
            }
        },

        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b><br/>'
        },
    })
    chart.addSeries({
        name: 'Errors',
        data: pie_data,
    }, false)
    var drill_series = []
    $.each(pie_drill_data, function(id, data){
        drill_series.push({
            id: id,
            data: data
        })
    })
    chart.options.drilldown = Highcharts.merge(chart.options.drilldown, {series: drill_series})

    console.log('redraw')
    chart.redraw()
    Highcharts.addEvent(chart.drilldown, 'drilldown', function (e) {console.log('drilldown'); });

}


$('#drilldown').click(function() {
    var t = 'test';
})

$('#update').click(function() {
  var t = 'test';
})