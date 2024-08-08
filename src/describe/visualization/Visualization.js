import React from 'react';    
import { Result, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import Chart from './Chart';


export default function Visualization(props) {
  
  if (props.visualization === 'loading') {
    const antIcon = (
      <LoadingOutlined style={{fontSize: 24}} spin />
    );
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Spin indicator={antIcon} />
      </div>
    );
  } else if (props.visualization === 'error') {
    return (
      <div style={{height: '100%'}}>
        <Result
          status='error'
          title='Unsupported Chart Configuration'
          subTitle='Please choose another chart.'
        >
        </Result>
      </div>
    );
  } else if (props.visualization.id) {
    return (
      <div style={{height: '100%'}}>
        <Chart
          options={props.visualization}
          visualCues={props.visualCues}
          visualCue={props.visualCue}
          toolbarOptions={props.toolbarOptions}
        />
      </div>
    );
  } else {
    return (
      <div style={{height: '100%'}}></div>
    );
  }
}