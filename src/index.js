import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter } from 'react-router-dom';
import LE_DEVOIR_DATA from './assets/LeDevoir.json';
import RADIO_CANADA_DATA from './assets/RadioCanada.json';
import RADIO_CANADA_DATA_25 from './assets/RadioCanada25.json';

export const Context = React.createContext();

const Provider = (props) => {
  const [language, setLanguage] = useState('en');
  const [descriptionState, setDescriptionState] = useState({});

  const [importState, setImportState] = useState({
    charts: [],
    pageNumber: 1,
    searchValue: ''
  });

  const [leDevoirState, setLeDevoirState] = useState({
    charts: LE_DEVOIR_DATA.data,
    pageNumber: 1,
    types: [],
    searchValue: ''
  });
  const [radioCanadaState, setRadioCanadaState] = useState({
    charts: RADIO_CANADA_DATA.data,
    pageNumber: 1,
    types: [],
    searchValue: ''
  });
  const [radioCanadaState25, setRadioCanadaState25] = useState({
    charts: RADIO_CANADA_DATA_25.data,
    pageNumber: 1,
    types: [],
    searchValue: ''
  })

  return (
    <Context.Provider value={{
      languageContext: [language, setLanguage],
      descriptionContext: [descriptionState, setDescriptionState],
      importContext: [importState, setImportState],
      leDevoirContext: [leDevoirState, setLeDevoirState],
      radioCanadaContext: [radioCanadaState, setRadioCanadaState],
      radioCanadaContext25: [radioCanadaState25, setRadioCanadaState25]
    }}>
      {props.children}
    </Context.Provider>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter basename={process.env.REACT_APP_BASENAME}>
      <Provider>
        <App />
      </Provider>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
