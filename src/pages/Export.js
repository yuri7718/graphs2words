import React, { useState } from 'react';
import { Card, Col, Button, List, Row, Typography, Tooltip } from 'antd';
import { EditOutlined,SaveOutlined, CopyOutlined} from '@ant-design/icons'
import { Context } from '../index';
import SEMANTIC_LEVEL from '../assets/semanticLevel.json';


const { Paragraph } = Typography;
const { Meta } = Card;

const LANGUAGES = ['en', 'fr'];

export default function Export({description, ...props}) {
  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const [editing, setEditing] = useState(Object.fromEntries(Object.keys(SEMANTIC_LEVEL[language]).map(layer => [layer, false])));
  const [copying, setCopying] = useState(Object.fromEntries(Object.keys(SEMANTIC_LEVEL[language]).map(layer => [layer, false])));

  const [editableStr, setEditableStr] = useState(
    Object.keys(description).reduce((editableStr, key) => {
      editableStr[key] = {}
      LANGUAGES.forEach(lang => {
        editableStr[key][lang] = description[key].map(x => x.text[lang]).join(' ');
      })
      return editableStr;
    }, {})
  );

  const onChange = (layer, str) => {
    const text = editableStr[layer];
    text[language] = str;
    setEditableStr(prev => ({...prev, [layer]: text}));
  };


  const onCopy = (key) => {
    setCopying(prev => ({...prev, [key]: true}));
    navigator.clipboard.writeText(editableStr[key][language]);
    const delay = 2000;
    setTimeout(() => {
      setCopying(prev => ({...prev, [key]: false}));
    }, delay);
  };
  
  const onCopyDescription = () => {
    const finalDescription = Object.keys(editableStr).map(key => editableStr[key][language]).join('\n');
    navigator.clipboard.writeText(finalDescription);
  };

  return (
    <div>
      <Row gutter={[16,16]}>
        <Col span={24} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100vh'}}>
          {Object.keys(SEMANTIC_LEVEL[language]).map(key => 
            <Card
              key={key}
              style={{width: '50%', margin: 30}}
              actions={[
                <EditOutlined key='edit' onClick={() => {setEditing(prev => ({...prev, [key]: true}))}}/>,
                <Tooltip title='Copied' trigger='click' open={copying[key]}>
                  <CopyOutlined key='copy' onClick={() => onCopy(key)} />
                </Tooltip>
              ]}
            >
              <Meta
                title={SEMANTIC_LEVEL[language][key]}
                description={
                  <Paragraph
                    style={{textAlign: 'left', padding: 30}}
                    editable={{
                      icon: <></>,
                      onChange: (str) => onChange(key, str),
                      editing: editing[key],
                      onEnd: () => {setEditing(prev => ({...prev, [key]: false}))}
                    }}>
                    {editableStr[key][language]}
                  </Paragraph>
                }
              />
            </Card>  
          )}
          {/* <Button type="primary" style={{margin: 30}} onClick={onCopyDescription}>Copy the whole description</Button> */}
        </Col>
      </Row>
    </div>
  );

}