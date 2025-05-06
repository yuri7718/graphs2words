import React from 'react';
import { Menu } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { Context } from '../index';
import navigationTranslation from '../translation/navigation.json';

const authStyle = {marginLeft: 'auto'};

export default function Navigation({token, setToken}) {

  const {importContext, languageContext} = React.useContext(Context);
  const [importState, setImportState] = importContext
  const [language, setLanguage] = languageContext;
  const translation = navigationTranslation[language];

  const location = useLocation();

  const onLanguageClick = (e) => {setLanguage(e.key)};

  const logout = () => {
    setToken(null);
    setImportState({
      charts: [],
      pageNumber: 1,
      searchValue: ''
    });
  };
  const authComponent = token != null ?
    {
      label: <>{translation.logout}</>,
      key: 'logout',
      onClick: logout,
      style: authStyle
    } :
    {label: <Link to='/login'>{translation.login}</Link>, key: '/login', style: authStyle};
  
  const menuItems = [
    {label: <Link to='/'>{translation.home}</Link>, key: '/'},
    {label: <Link to='/import'>{translation.import}</Link>, key: '/import'},
    {label: <Link to='/export'>{translation.export}</Link>, key: '/export'},
    {
      label: <>{translation.samples}</>, key: '/dataset', children: [
        {label: <Link to='/dataset' state={{data: 'le-devoir'}}>Le Devoir</Link>, key: 'le-devoir'},
        {label: <Link to='/dataset' state={{data: 'radio-canada'}}>Radio Canada</Link>, key: 'radio-canada'},
        {label: <Link to='/dataset' state={{data: 'radio-canada-25'}}>Radio Canada 2025</Link>, key: 'radio-canada-25'}
      ]
    },
    {
      label: <>{translation.language} <DownOutlined /></>, key: 'lang', children: [
        {label: 'English', key: 'en', onClick: onLanguageClick},
        {label: 'Français', key: 'fr', onClick: onLanguageClick}
      ]
    },
    authComponent
  ];

  return (
    <div>
      <Menu theme='dark' mode='horizontal' selectedKeys={[location.pathname]} items={menuItems} />
    </div> 
  );
}