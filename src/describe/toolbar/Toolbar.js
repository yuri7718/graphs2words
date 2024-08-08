import React, { memo } from 'react';
import { Divider, Select, Table, Tag, Typography } from 'antd';
import { Context } from '../../index';
import SEMANTIC_LEVEL from "../../assets/semanticLevel.json";
import './Toolbar.css';

const { Text } = Typography;

function Toolbar(props) {

  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const semanticLevel = SEMANTIC_LEVEL[language];

  const columns1 = [
    {
      title: semanticLevel.L1,
      dataIndex: 'title',
      key: 'title',
      render: (text) => <Tag className='tree-L1'>{text[language]}</Tag>,
      defaultFilteredValue: ['show'],
      onFilter: (value, record) => record[value] != false
    },
    {
      dataIndex: 'comparison',
      key: 'comparison',
      width: '40%',
    }
  ];

  const tagRender = (props) => {
    const { label, value, closable, onClose } = props;
    const onPreventMouseDown = (event) => {
      event.preventDefault();
      event.stopPropagation();
    };
    return (
      <Tag
        onMouseDown={onPreventMouseDown}
        closable={closable}
        onClose={onClose}
        style={{marginRight: 3}}
      >
        <Text style={{width: 100}} ellipsis={{tooltip: label}}>{label}</Text>
      </Tag>
    );
  };

  const columns2 = [
    {
      title: semanticLevel.L2,
      dataIndex: 'title',
      key: 'title',
      render: (text) => {
        return (
          <Tag className='tree-L2'>
            <Text style={{maxWidth: 120, color: '#389e0d'}} ellipsis={{tooltip: text[language]}}>{text[language]}</Text>
          </Tag>
        );
      },
      defaultFilteredValue: ['show'],
      onFilter: (value, record) => record[value] != false
    },
    {
      dataIndex: 'comparison',
      key: 'comparison',
      width: '40%',
      render: (options) => {
        if (options && options.length > 0) {
          const key = options[0].selectKey;
          const defaultValue = props.selectedToolbarOptions[key] || options.map(x => x.value);
          return (
            <Select
              style={{minWidth: '100%'}}
              mode='tags'
              allowClear
              defaultValue={defaultValue}
              onChange={(value, option) => {props.onSelectChange(key, value, option)}}
              options={options}
              tagRender={tagRender}
            />
          )
        } else {return <></>}
      }
    }
  ];

  const columns3 = [
    {
      title: semanticLevel.L3,
      dataIndex: 'title',
      key: 'title',
      render: (text) => <Tag className='tree-L3'>{text[language]}</Tag>,
      defaultFilteredValue: ['show'],
      onFilter: (value, record) => record[value] != false
    },
    {
      dataIndex: 'comparison',
      key: 'comparison',
      width: '40%'
    }
  ];

  return (
    <div
      id='scrollableDiv'
      style={{
        height: 'calc(100vh - 46px - 48px)',
        overflow: 'auto',
        padding: '0 16px',
        border: '1px solid rgba(140, 140, 140, 0.35)'
      }}
    >
      {
        props.schema.L1 && props.schema.L1.length > 0 ? ( <Table
          key='tree-L1'
          columns={columns1}
          expandable={{defaultExpandAllRows: true}}
          pagination={false}
          rowSelection={{
            checkStrictly: false,
            onChange: (selectedRowKeys, selectedRows) => {props.onCheck(selectedRowKeys, 'L1');},
            selectedRowKeys: props.selectedRowKeys.L1
          }}
          dataSource={props.schema.L1}
        />) : (<Table key='empty-L1' columns={columns1} />)
      }
      <Divider />
      {
        props.schema.L2 && props.schema.L2.length > 0 ? (
          <Table
            key='tree-L2'
            columns={columns2}
            expandable={{defaultExpandAllRows: true}}
            pagination={false}
            rowSelection={{
              checkStrictly: false,
              onChange: (selectedRowKeys, selectedRows) => {props.onCheck(selectedRowKeys, 'L2');},
              selectedRowKeys: props.selectedRowKeys.L2
            }}
            dataSource={props.schema.L2}
          />
        ) : (<Table key='empty-L2' columns={columns2} />)
      }
      <Divider />
      {
        props.schema.L3 && props.schema.L3.length > 0 ? (
          <Table
            key='tree-L3'
            columns={columns3}
            expandable={{defaultExpandAllRows: true}}
            pagination={false}
            rowSelection={{
              checkStrictly: false,
              onChange: (selectedRowKeys, selectedRows) => {props.onCheck(selectedRowKeys, 'L3');},
              selectedRowKeys: props.selectedRowKeys.L3
            }}
            dataSource={props.schema.L3}
          />
        ) : (<Table key='empty-L3' columns={columns3} />)
      }
    </div>
  );
};

export default memo(Toolbar);