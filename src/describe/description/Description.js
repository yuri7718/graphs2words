import Container from './dnd/Container';

export default function Description(props) {

  const ids = Object.keys(props.items);

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
      {ids.map(id => (<Container key={id} id={id} {...props} />))}
    </div>
  );
}