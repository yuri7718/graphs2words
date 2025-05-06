import React from 'react';
import { useLocation } from 'react-router-dom';
import { Context } from '../index';
import SelectChart from '../dataset/SelectChart';
import LE_DEVOIR_DATA from '../assets/LeDevoir.json';
import RADIO_CANADA_DATA from '../assets/RadioCanada.json';
import RADIO_CANADA_DATA_25 from '../assets/RadioCanada25.json';

export default function Dataset(props) {

  const { state } = useLocation();
  
  const {leDevoirContext, radioCanadaContext, radioCanadaContext25} = React.useContext(Context);
  const [leDevoirState, setLeDevoirState] = leDevoirContext;
  const [radioCanadaState, setRadioCanadaState] = radioCanadaContext;
  const [radioCanadaState25, setRadioCanadaState25] = radioCanadaContext25;

  if (state == null) {
    return (
      <div style={{height: '100vh'}}>
        Plaese select a dataset
      </div>
    )
  }
  switch(state.data) {
    case 'le-devoir':
      return (
        <div>
          <SelectChart
            state={leDevoirState}
            setState={setLeDevoirState}
            dataset={LE_DEVOIR_DATA.data}
            datasetKey={'le-devoir'}
            onSelectChart={props.onSelectChart}
          />
        </div>
      );
    case 'radio-canada':
      return (
        <div>
          <SelectChart
            state={radioCanadaState}
            setState={setRadioCanadaState}
            dataset={RADIO_CANADA_DATA.data}
            datasetKey={'radio-canada'}
            onSelectChart={props.onSelectChart}
          />
        </div>
      );
    case 'radio-canada-25':
      return (
        <div>
          <SelectChart
            state={radioCanadaState25}
            setState={setRadioCanadaState25}
            dataset={RADIO_CANADA_DATA_25.data}
            datasetKey={'radio-canada-25'}
            onSelectChart={props.onSelectChart}
          />
        </div>
      )
  }
}