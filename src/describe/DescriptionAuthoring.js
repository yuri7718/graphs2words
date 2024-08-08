import React, { useState, useEffect, memo, useMemo, useCallback,  } from 'react';
import { Row, Col, Card } from 'antd';
import { Context } from '../index';
import Toolbar from './toolbar/Toolbar';
import Visualization from './visualization/Visualization';
import Description from './description/Description';
import SEMANTIC_LEVEL from '../assets/semanticLevel.json';

function DescriptionAuthoring({description, setDescription, state, setState}) {

  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const [visualCue, setVisualCue] = useState();
  const [toolbarOptions, setToolbarOptions] = useState({});

  const setParagraphClickTriggerStr = (layer, id, str) => {
    const container = description[layer];
    for (let item of container) {
      if (item.id === id) {
        item.text[language] = str;
        break;
      }
    }
    setDescription(prev => ({...prev, [layer]: container}));
  }
  

  const setDescriptionUsingKeys = (checkedKeys, layer) => {
    const descriptions = checkedKeys.filter(key => key in state.visDescription).map(key => {
      try {
        return state.visDescription[key];
      } catch (error) {
        return {id: key, tag: {en: key, fr: key}, text: {en: key, fr: key}};
      }
    });
    setDescription(prev => ({...prev, [layer]: descriptions}));
  };

  const onCheck = useCallback((checkedKeys, layer) => {
    setDescriptionUsingKeys(checkedKeys, layer);
    
    const selectedRowKeys = state.selectedRowKeys;
    selectedRowKeys[layer] = checkedKeys;
    setState(prev => ({...prev, selectedRowKeys: selectedRowKeys}));
  }, [state.visDescription])


  const onToolbarChange = (key, value, options) => {
    setToolbarOptions(prev => ({...prev, [key]: options}));
    try {
      const item = state.visDescription[key];
      const textEn = options.map(x => x.values.en).join('; ');
      const textFr = options.map(x => x.values.fr).join('; ');
      item.text.en = textEn;
      item.text.fr = textFr;
      
      const selectedToolbarOptions = state.selectedToolbarOptions;
      selectedToolbarOptions[key] = value;

      setState(prev => ({
        ...prev,
        visDescription: state.visDescription,
        selectedToolbarOptions: selectedToolbarOptions}
      ));
    } catch (error) { console.error(error); }
  }

  const getDefaultSelectValue = (schema) => {

    const getComparison = (schema) => {
      const comparison = [];
      schema.forEach(x => {
        if (Object.keys(x).includes('children')) {
          comparison.push(...getComparison(x.children))
        } else if (Object.keys(x).includes('comparison')) {
          comparison.push(...x.comparison);
        }
      })
      return comparison;
    };
    
    return getComparison(schema).reduce((options, x) => {
      if (Object.keys(options).includes(x.selectKey)) {
        options[x.selectKey].push(x);
      } else {
        options[x.selectKey] = [x];
      }
      return options;
    }, {});
  };


  useEffect(() => {
    if (state.schema && state.schema.L2) {
      setToolbarOptions(getDefaultSelectValue(state.schema.L2));
    }
  }, [state.schema])

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Row gutter={[16,16]}>
            <Col span={7}>
              <Card style={{height: 'calc(100vh - 46px)'}}>
                <Toolbar
                  schema={state.schema || {L1: [], L2: [], L3: []}}
                  onCheck={onCheck}
                  selectedRowKeys={state.selectedRowKeys}
                  onSelectChange={onToolbarChange}
                  selectedToolbarOptions={state.selectedToolbarOptions}
                />
              </Card>
            </Col>
            <Col span={10} >
              <Card style={{height: 'calc(100vh - 46px)'}}>
                <Description
                  items={description}
                  setItems={setDescription}
                  setParagraphClickTriggerStr={setParagraphClickTriggerStr}
                  setVisualCue={setVisualCue}
                />
                </Card>
              </Col>
            <Col span={7}>
              <Card style={{height: 'calc(100vh - 46px)'}}>
                <Visualization
                  visualization={state.visualization || {}}
                  visualCues={state.visualCues || {}}
                  visualCue={visualCue}
                  toolbarOptions={toolbarOptions || {}} />
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
}

export default memo(DescriptionAuthoring);