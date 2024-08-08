import React, {useEffect, useState} from 'react';
import ImportChart from '../import/Import';
import { Context } from '../index';
export default function Import(props) {

  const {importContext} = React.useContext(Context);
  const [importState, setImportState] = importContext;

  return (
    <div>
      <ImportChart
        state={importState}
        setState={setImportState}
        onSelectChart={props.onSelectChart}
        token={props.token}
      />
    </div>
  );

}