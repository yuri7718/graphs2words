import React, { useEffect, useState } from 'react';
import { Card } from 'antd';
import {
  DndContext,
  closestCenter,
  MouseSensor,
  TouchSensor,
  DragOverlay,
  useSensor,
  useSensors,
  rectIntersection,
  KeyboardSensor
} from '@dnd-kit/core';
import { arrayMove, SortableContext, rectSortingStrategy, sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Context } from '../../../index';
import SortableItem from './SortableItem';
import Item from './SortableItem';
import semanticLevel from '../../../assets/semanticLevel.json'

export default function Container(props) {

  const {languageContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const sensors = useSensors(
    useSensor(MouseSensor),
    useSensor(TouchSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates
    })
  );

  //const [items, setItems] = useState(props.items);
  const [activeItem, setActiveItem] = useState(null);

  /**
   * DndContext
   */
  const findActiveItem = (activeId) => {
    const items = props.items[activeId.split('-')[0]];
    for (let item of items) {
      if (item.id === activeId) {return item;}
    }
  };

  const handleDragStart = (event) => {
    setActiveItem(findActiveItem(event.active.id))
  };

  const handleDragOver = (event) => {
    const {active, over} = event;
    if (over === null) return;
    if (active.id !== over.id) {
      const layer = active.id.split('-')[0];
      props.setItems(items => {
        const oldIdx = items[layer].map(x => x.id).indexOf(active.id);
        const newIdx = items[layer].map(x => x.id).indexOf(over.id);
        return {...items, [layer]: arrayMove(items[layer], oldIdx, newIdx)};
      });
    }
  }


  const handleDragEnd = (event) => {
    const {active, over} = event;
    if (over === null) return;
    if (active.id !== over.id) {
      // setItems(items => {
      //   const oldIdx = items.map(x => x.id).indexOf(active.id);
      //   const newIdx = items.map(x => x.id).indexOf(over.id);
      //   return arrayMove(items, oldIdx, newIdx);
      // });
      const layer = active.id.split('-')[0];
      props.setItems(items => {
        const oldIdx = items[layer].map(x => x.id).indexOf(active.id);
        const newIdx = items[layer].map(x => x.id).indexOf(over.id);
        return {...items, [layer]: arrayMove(items[layer], oldIdx, newIdx)};
      });
    }
    setActiveItem(null)
  };

  const handleDragCancel = () => setActiveItem(null);


  return (
    <div>
      <Card title={semanticLevel[language][props.id]}>
        <DndContext
          sensors={sensors}
          collisionDetection={rectIntersection}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
          onDragCancel={handleDragCancel}
        >
        <SortableContext items={props.items[props.id]} strategy={rectSortingStrategy}>
          <div style={{textAlign: 'left'}}>
            {props.items[props.id].map(x => {
              return (
              <SortableItem
                key={x.id}
                layerId={props.id}
                id={x.id}
                tag={x.tag}
                text={x.text}
                setParagraphClickTriggerStr={props.setParagraphClickTriggerStr}
                setVisualCue={props.setVisualCue}
              />
            )})}
          </div>
        </SortableContext>
        <DragOverlay>
          {activeItem ? <Item style={{textAlign: 'left'}} layerId={props.id} id={activeItem.id} tag={activeItem.tag} text={activeItem.text} isDragging /> : null}
        </DragOverlay>
        </DndContext>
      </Card>
    </div>
  );
};