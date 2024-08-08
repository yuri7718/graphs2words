import React, { useState } from 'react';
import { Pagination, Row, Col, Card, Image, Divider, Input, Button, Empty, Select, message } from 'antd';
import { Link } from "react-router-dom";
import { Context } from '../index';
import axios from 'axios';
import selectTranslation from '../translation/selectChart.json';

const { Search } = Input;

const axiosHttp = axios.create({
  baseURL: process.env.REACT_APP_BASE_URL
});

const PAGE_SIZE = 9;
const TYPE_OPTIONS = [
  'd3-bars', 'd3-bars-split', 'd3-bars-stacked', 'd3-bars-grouped',
  'column-chart', 'grouped-column-chart', 'stacked-column-chart',
  'd3-area', 'd3-lines', 'd3-pies'
];

const FALLBACK = 'data:image/png;base64,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';


export default function SelectChart({state, setState, dataset, datasetKey, onSelectChart}) {
  /**
   * keys for state:
   * charts
   * pageNumber
   * types
   * selectedChart
   * searchValue
   */

  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;
  const translation = selectTranslation[language];

  // filter chart types
  const filteredOptions = TYPE_OPTIONS.filter(x => !state.types.includes(x));
  const onSelectChange = (value) => {
    setState(prev => ({
      ...prev,
      types: value,
      charts: value.length === 0 ? dataset : dataset.filter(x => value.includes(x.type)),
      pageNumber: 1
    }));
  };

  const onImgClick = (e) => {
    const idx = e.currentTarget.attributes.idx.value;
    const chart = state.charts[idx];
    setState(prev => ({...prev, selectedChart: chart}));
  };

  // search chart id
  const [messageApi, contextHolder] = message.useMessage();
  const [searchDisabled, setSearchDisabled] = useState(false);
  const showError = () => {
    messageApi.open({type: 'error', content: translation.searchError});
  };
  
  const onSearch = async (value) => {
    setSearchDisabled(true);
    setState(prev => ({...prev, searchValue: value}));

    axiosHttp.post('/chart/v2', {
      chartId: value,
      datasetKey: datasetKey
    }).then(response => {
      setState(prev => ({...prev, selectedChart: response.data}));
      setSearchDisabled(false);
    }).catch(error => {
      setState(prev => ({...prev, selectedChart: null}));
      showError();
      setSearchDisabled(false);
    });
  };

  const isValidChart = (chart) => {
    return chart == null ? false : dataset.map(x => x.publicId).includes(chart.publicId);
  };

  return (
    <div>
      {contextHolder}
      <Row gutter={[16,16]}>
        <Col span={16}>
          <Card style={{height: 'calc(100vh - 46px)'}}>
            <Row gutter={[32,32]}>
              <Col span={24}>
                {datasetKey}
                <Select
                  mode='multiple'
                  value={state.types}
                  onChange={onSelectChange}
                  style={{width: '100%'}}
                  options={filteredOptions.map(x => ({value: x, label: x}))}
                />
              </Col>
              <Col span={24}>
                <Row gutter={[48,64]}>
                  {state.charts.filter((_,i) => {
                    return (state.pageNumber - 1) * PAGE_SIZE <= i && i < state.pageNumber * PAGE_SIZE;
                  }).map((x,i) => 
                    <Col span={8} key={x['publicId']}>
                      <Image
                        height={150}
                        width={150}
                        src={x['thumbnail']}
                        fallback={FALLBACK}
                        preview={false}
                        idx={(state.pageNumber - 1) * PAGE_SIZE + i}
                        onClick={onImgClick}
                        style={{cursor: 'pointer'}}
                      />
                      <p>{x['publicId']}</p>
                      <p>{x['type']}</p>
                    </Col>
                  )}
                </Row>
              </Col>
            </Row>
            <Divider />
            <Pagination
              pageSize={PAGE_SIZE}
              current={state.pageNumber}
              total={state.charts.length}
              onChange={(page) => {setState(prev => ({...prev, pageNumber: page}));}}
              showQuickJumper={true}
              showSizeChanger={false}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card style={{height: 'calc(100vh - 46px)'}}>
            <Row gutter={[32,32]}>
              <Col span={24}>
                &nbsp;
                <Search
                  key={datasetKey}
                  defaultValue={state.searchValue}
                  placeholder={translation.searchPlaceholder}
                  onSearch={onSearch}
                  disabled={searchDisabled}
                  enterButton
                />
              </Col>
              <Col span={24}>
                <div style={{height: 836, display: 'flex', justifyContent: 'center', flexDirection: 'column'}}>
                  {state.selectedChart ? <Image src={state.selectedChart.thumbnail} /> : <Empty />}
                </div>
              </Col>
            </Row>
            <Divider />
            <Link to='/'>
              <Button
                type='primary'
                onClick={() => {onSelectChart(state.selectedChart['publicId'], datasetKey)}}
                disabled={!isValidChart(state.selectedChart)}
              >
                {translation.select}
              </Button>
            </Link>
          </Card>
        </Col>
      </Row>
    </div>
  );
}