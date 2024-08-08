import React, { useState, useEffect, useRef } from "react";
import * as echarts from 'echarts';
import Parser from 'html-react-parser';


const CHART_STYLE = {
  'default': {height: '100%'},
  'highlighted': {height: '100%', background: '#e0e0e0'}
}

const TITLE_STYLE = {
  'default': {textAlign: 'left', fontSize: '20px', fontWeight: 'bold'},
  'highlighted': {textAlign: 'left', fontSize: '20px', fontWeight: 'bold', backgroundColor: '#ffff00'}
};

const INTRO_STYLE = {
  'default': {textAlign: 'left'},
  'highlited': {textAlign: 'left', backgroundColor: '#ffff00'}
};

const NOTES_STYLE = {
  'default': {textAlign: 'left'},
  'highlited': {textAlign: 'left', backgroundColor: '#ffff00'}
}

const DECAL = {
  symbol: 'rect',
  dashArrayX: [1, 0],
  dashArrayY: [4, 3],
  rotation: -Math.PI / 4
}

function Chart({visualCue, toolbarOptions, ...props}) {

  const [defaultOption, setDefaultOption] = useState();
  const [specificVisualCues, setSpecificVisualCues] = useState(props.visualCues)

  // const disableLegend = (e) => {
  //   if (e !== null) {
  //     echartRef = e.getEchartsInstance();
  //     echartRef.on('legendselectchanged', function(params) {
  //      suppressSelection(echartRef, params);
  //     })
  //   }
  // }

  // const suppressSelection = (echart, params) => {
  //   echart.dispatchAction({
  //     type: 'legendSelect',
  //     name: params.name
  //   });
  // }
 
  
  const chartRef = useRef();
  const [chart, setChart] = useState();
  
  useEffect(() => {
    const chart = echarts.init(chartRef.current);
    switch(props.options.type) {
      case 'd3-bars':
        var option = structuredClone(props.options.option);
        var highlightedSeries = props.options.option.yAxis.axisLabel.formatter;
        option.yAxis.axisLabel.formatter = (value) => highlightedSeries.includes(value) ? `{highlighted|${value}}` : value;
        setDefaultOption(option);
        chart.setOption(option, {notMerge: true});
        break;
      case 'd3-bars-split':
        var tmpOption = structuredClone(props.options.option);
        tmpOption.series.forEach((x,i) => {x['itemStyle'] = {color: d => props.options.color[i][d.dataIndex]}})
        setDefaultOption(tmpOption);
        chart.setOption(tmpOption);
        break;
      case 'd3-bars-stacked':
        var tmpOption = structuredClone(props.options.option);
        tmpOption.series.forEach((x,i) => {
          x['label'] = {
            show: true,
            formatter: d => Math.abs(d.value[i+1]) > props.options.threshold ? d.value[i+1].toFixed(2) : ''
          }
        });
        setDefaultOption(tmpOption);
        chart.setOption(tmpOption);
        break;
      case 'd3-bars-grouped':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'column-chart':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'grouped-column-chart':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'stacked-column-chart':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'd3-area':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'd3-lines':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      case 'd3-pies':
        setDefaultOption(props.options.option);
        chart.setOption(props.options.option);
        break;
      default:
        break;
    }
    setChart(chart);
  }, [props.options.id])

  useEffect(() => {
  }, [toolbarOptions]);

  useEffect(() => {
    if (chart != null && defaultOption != null) {
      chart.setOption(defaultOption, {notMerge: true});
    } 
    if (visualCue == null) return;
    
    if (props.options.type === 'd3-bars' || props.options.type === 'column-chart') {
      switch(visualCue) {
        case 'L1-4-0':
          chart.setOption({xAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-4-1':
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-5':
          chart.setOption({aria: {'enabled': true, 'decal': {'show': true, 'decals': [DECAL]}}});
          break;
        case 'L2-2-0':
          chart.setOption({series: {markLine: {data: [{type: 'average'}]}}})
          break;
        case 'L2-2-2':
          chart.setOption({series: {markLine: {data: [{type: 'median'}]}}})
          break;
        default:
          if (visualCue in specificVisualCues) {
            if (/^L1-5(-\d+)*$/.test(visualCue)) {
              chart.setOption({aria: specificVisualCues[visualCue]});
            } else {
              chart.setOption({series: specificVisualCues[visualCue]});
            }
          }
      }
    } else if (props.options.type === 'd3-bars-split') {
      switch(visualCue) {
        case 'L1-4-0':
          var title = chart.getOption().title;
          title.forEach(x => x['backgroundColor'] = '#ffff00');
          chart.setOption({title: title});
          break;
        case 'L1-4-1':
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L2-1-0-0': case 'L2-1-1-0':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[i]['data'][idx]['itemStyle']['decal'] = DECAL;
            });
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-0-1': case 'L2-1-1-1':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[idx]['data'][i]['itemStyle']['decal'] = DECAL;
            });
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-0-0':
          if (visualCue in toolbarOptions) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'average'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-2-0':
          if (visualCue in toolbarOptions) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'median'}]};});
            chart.setOption({series: series});
          }
          break;
        default:
          if (visualCue in specificVisualCues) {
            chart.setOption({series: specificVisualCues[visualCue]});
          }
      }
    } else if (props.options.type === 'd3-bars-stacked' || props.options.type === 'stacked-column-chart') {
      switch(visualCue) {
        case 'L1-4-0':
          chart.setOption({xAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-4-1':
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L2-1-0-1': case 'L2-1-1-1':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[i]['data'][idx]['itemStyle'] = {decal: DECAL};
            });
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-0-2': case 'L2-1-1-2':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[idx]['data'][i]['itemStyle'] = {decal: DECAL};
            });
            chart.setOption({series: series});
          }
          break;
        default:
          if (visualCue in specificVisualCues) {
            console.log(specificVisualCues[visualCue]);
            chart.setOption({series: specificVisualCues[visualCue]});
          };
      }
    } else if (props.options.type === 'd3-bars-grouped' || props.options.type === 'grouped-column-chart') {
      switch(visualCue) {
        case 'L1-4-0':
          chart.setOption({xAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-4-1':          
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L2-1-0-0':
          if (visualCue in toolbarOptions) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'max'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-0-1':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[idx]['data'][i]['itemStyle'] = {decal: DECAL};
            });
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-1-0':
          if (visualCue in toolbarOptions) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'min'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-1-1':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {
              let idx = specificVisualCues[visualCue][i];
              series[idx]['data'][i]['itemStyle'] = {decal: DECAL};
            });
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-0-0':
          if (visualCue in toolbarOptions) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'average'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-0-1': case 'L2-2-2-1':
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var data = indices.map(i => {
              if (props.options.type === 'grouped-column-chart') {
                return Array(2).fill({
                  xAxis: i,
                  yAxis: specificVisualCues[visualCue][i],
                  itemStyle: {borderWidth: 1, borderType: 'dashed'}
                });
              }
              if (props.options.type === 'd3-bars-grouped') {
                return Array(2).fill({
                  xAxis: specificVisualCues[visualCue][i],
                  yAxis: i,
                  itemStyle: {borderWidth: 1, borderType: 'dashed'}
                });
              }
            })
            chart.setOption({series: {markArea: {data: data}}});
          }
          break;
        case 'L2-2-2-0':
          var indices = toolbarOptions['L2-2-2-0'].map(x => x.seriesKey);
          var series = chart.getOption().series;
          indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'median'}]};});
          chart.setOption({series: series});
          break;
        default:
          if (visualCue in specificVisualCues) {
            chart.setOption({series: specificVisualCues[visualCue]});
          }
      }
    } else if (props.options.type === 'd3-area') {
      switch(visualCue) {
        case 'L1-4-0':
          chart.setOption({xAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-4-1':
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L2-1-0':
          chart.setOption({series: {markPoint: {data: [{type :'max'}]}}});
          break;
        case 'L2-1-1':
          chart.setOption({series: {markPoint: {data: [{type :'min'}]}}});
          break;
        case 'L2-1-0-0': case 'L2-1-0-1': case 'L2-1-1-0': case 'L2-1-1-1':
          // extrema for multivariate data
          if (visualCue in toolbarOptions && visualCue in specificVisualCues) {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markPoint'] = specificVisualCues[visualCue][i];})
            chart.setOption({series: series})
          }
          break;
        case 'L2-2-0':
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markLine: {data: [{type: 'average'}]}}});
          } else {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'average'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-2':
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markLine: {data: [{type: 'median'}]}}});
          } else {
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            var series = chart.getOption().series;
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'median'}]};});
            chart.setOption({series: series});
          }
          break;
        default:
          if (visualCue in specificVisualCues) {
            chart.setOption({series: specificVisualCues[visualCue]});
          }
      }
    } else if (props.options.type === 'd3-lines') {
      switch(visualCue) {
        case 'L1-4-0':
          chart.setOption({xAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-4-1':
          chart.setOption({yAxis: {axisLabel: {backgroundColor: '#ffff00'}}});
          break;
        case 'L1-5':
          chart.setOption({series: {lineStyle: {shadowColor: '#ffff00', shadowBlur: 10}}});
          break;
        case 'L2-1-0':
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markPoint: {data: [{type: 'max'}]}}});
          } else {
            var series = chart.getOption().series;
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            indices.forEach(i => {series[i]['markPoint'] = {data: [{type: 'max'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-1-1': 
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markPoint: {data: [{type: 'min'}]}}});
          } else {
            var series = chart.getOption().series;
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            indices.forEach(i => {series[i]['markPoint'] = {data: [{type: 'min'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-0':
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markLine: {data: [{type: 'average'}]}}})
          } else {
            var series = chart.getOption().series;
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'average'}]};});
            chart.setOption({series: series});
          }
          break;
        case 'L2-2-2': 
          if (!Object.keys(toolbarOptions).includes(visualCue)) {
            chart.setOption({series: {markLine: {data: [{type: 'median'}]}}})
          } else {
            var series = chart.getOption().series;
            var indices = toolbarOptions[visualCue].map(x => x.seriesKey);
            indices.forEach(i => {series[i]['markLine'] = {data: [{type: 'median'}]};});
            chart.setOption({series: series});
          }
          break;
        default:
          if (visualCue in specificVisualCues) {
            chart.setOption({series: specificVisualCues[visualCue]});
          }
      }
    } else if (props.options.type === 'd3-pies') {
      switch (visualCue) {
        default:
          if (visualCue in specificVisualCues) {
            chart.setOption({aria: specificVisualCues[visualCue]});
          }
      }
    }
  }, [visualCue])

  
  return (
    <div style={visualCue === 'L1-0' ? CHART_STYLE.highlighted: CHART_STYLE.default}>
      <div style={visualCue === 'L1-1' ? TITLE_STYLE.highlighted : TITLE_STYLE.default}>{Parser(props.options.title)}</div>
      <div style={visualCue === 'L1-2' ? INTRO_STYLE.highlited : INTRO_STYLE.default}>{Parser(props.options.intro)}</div>
      <div style={{height: '70%'}} ref={chartRef}></div>
      <div style={visualCue === 'L1-3' ? NOTES_STYLE.highlited : NOTES_STYLE.default}>{Parser(props.options.annotation)}</div>
    </div>
  );
}

export default Chart;