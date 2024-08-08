import React, { useEffect, useState } from 'react';
import { Button, Card, Form, Input, Row, Col } from 'antd';
import { useNavigate } from "react-router-dom";
import { Context } from '../index';
import axios from 'axios';
import loginTranslation from '../translation/login.json';

const axiosHttp = axios.create({
  baseURL: process.env.REACT_APP_BASE_URL
});

export default function Login({setToken}) {
  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const translation = loginTranslation[language];

  const [form] = Form.useForm();
  const [invalidToken, setInvalidToken] = useState(false);

  const navigate = useNavigate();

  const onFinish = (values) => {
    axiosHttp.post('/auth/login', {
      token: values.token
    }).then(response => {
      setToken(values.token);
      navigate('/import');
    }).catch(error => {
      setInvalidToken(true);
    })
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  const onChange = () => {
    if (invalidToken) {
      setInvalidToken(false);
    }
  };

  useEffect(() => {
    if (invalidToken) {
      form.validateFields(['token']);
    }
  }, [invalidToken]);

  return (
    <div>
      <Row>
        <Col span={24}>
          <Card style={{height: 'calc(100vh - 46px)', padding: 50, display: 'flex', justifyContent: 'center'}}>
            <Form
              form={form}
              name='login'
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
            >
              <Form.Item
                label='Datawrapper token'
                name='token'
                rules={[
                  {
                    required: true,
                    message: translation.missingToken},
                  {
                    validator: () => invalidToken ? Promise.reject(new Error()) : Promise.resolve(),
                    message: translation.invalidToken
                  }
                ]}
                onChange={onChange}
              >
                <Input.Password />
              </Form.Item>
              <Form.Item>
                <Button type='primary' htmlType='submit' style={{width: '100%'}}>{translation.submit}</Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
}