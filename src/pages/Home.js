import React, { useEffect } from 'react';
import DescriptionAuthoring from '../describe/DescriptionAuthoring';
import axios from 'axios';

export default function Home({chartId, isAuthenticated, token, datasetKey, ...props}) {

  /**
   * chartId
   * visualization
   * schema
   * visDescription
   * visualCues
   */
  useEffect(() => {
    const controller = new AbortController();
    if (chartId.length > 0 && chartId != props.state.chartId) {
      props.setState({visualization: 'loading'});
      props.setDescription({L1:[], L2: [], L3: []});

      if (isAuthenticated) {
        axios.post(
          `${process.env.REACT_APP_BASE_URL}/visualization/v3`,
          {chartId: chartId, token: token},
          {signal: controller.signal}
        ).then(response => {
          props.setState({
            chartId: chartId,
            visualization: response.data.visualize,
            schema: response.data.schema,
            visDescription: response.data.visDescription,
            visualCues: response.data.visualCue,
            selectedRowKeys: {L1: [], L2: [], L3:[]},
            selectedToolbarOptions: {}
          });
        }).catch(error => {
          if (error.code !== "ERR_CANCELED") {
            props.setState({visualization: 'error'});
          }
        });
      } else {
        axios.post(
          `${process.env.REACT_APP_BASE_URL}/visualization/v2`,
          {chartId: chartId, datasetKey: datasetKey},
          {signal: controller.signal}
        ).then(response => {
          props.setState({
            chartId: chartId,
            visualization: response.data.visualize,
            schema: response.data.schema,
            visDescription: response.data.visDescription,
            visualCues: response.data.visualCue,
            selectedRowKeys: {L1: [], L2: [], L3:[]},
            selectedToolbarOptions: {}
          });
        }).catch(error => {
          if (error.code !== "ERR_CANCELED") {
            props.setState({visualization: 'error'});
          }
        })
      }
    }

    return () => {controller.abort();}
  }, [chartId]);

  return (
    <div style={{height: 'calc(100vh - 46px)'}}>
      <DescriptionAuthoring {...props} />
    </div>
  );
}
