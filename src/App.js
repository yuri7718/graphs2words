import React, { useState } from 'react';
import { ConfigProvider, Layout } from 'antd';
import { Route, Routes } from 'react-router-dom';
import { Context } from './index';
import Navigation from './navigation/Navigation';
import PrivateRoute from './authentication/PrivateRoute';
import Home from './pages/Home';
import Import from './pages/Import';
import Export from './pages/Export';
import Dataset from './pages/Dataset';
import Login from './pages/Login';
import enUS from 'antd/es/locale/en_US';
import frCA from 'antd/es/locale/fr_CA';
import './App.css';

const LANGUAGES = {
  en: enUS,
  fr: frCA
};

function App() {

  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const [chartId, setChartId] = useState('');

  const [description, setDescription] = useState({L1: [], L2:[], L3: []});
  const [descriptionState, setDescriptionState] = useState({});

  const [isAuthenticated, setIsAuthenticated] = useState();
  const [datasetKey, setDatasetKey] = useState();

  const [token, setToken] = useState(null);


  const onImportChart = (chartId) => {
    setChartId(chartId);
    setIsAuthenticated(true);
  }

  const onSelectChartFromDataset = (chartId, datasetKey) => {
    setChartId(chartId);
    setDatasetKey(datasetKey);
    setIsAuthenticated(false);
  }

  return (
    <div className='App'>
      <Layout>
        <ConfigProvider locale={LANGUAGES[language]}>
          <Navigation token={token} setToken={setToken} />
            <Routes>
              <Route exact path='/' element={
                <Home
                  chartId={chartId}
                  isAuthenticated={isAuthenticated}
                  token={token}
                  datasetKey={datasetKey}
                  description={description}
                  setDescription={setDescription}
                  state={descriptionState}
                  setState={setDescriptionState}
                />
              }/>
              <Route element={<PrivateRoute token={token} />}>
                <Route exact path='/import' element={<Import onSelectChart={onImportChart} token={token} setToken={setToken} />} />
              </Route>
              <Route exact path='/export' element={<Export description={description} />}></Route>
              <Route exact path='/dataset' element={<Dataset onSelectChart={onSelectChartFromDataset} />}></Route>
              <Route exact path='/login' element={<Login setToken={setToken} />} />
            </Routes>
        </ConfigProvider>
      </Layout>
    </div>
  );
}

export default App;