import React, { forwardRef } from "react";
import { Tag, Typography } from 'antd';
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import './SortableItem.css';
import { Context } from '../../../index';
const { Paragraph } = Typography;

export const Item = forwardRef(({isDragging, ...props}, ref) => {
  const {languageContext, descriptionContext} = React.useContext(Context);
  const [language, setLanguage] = languageContext;

  const inlineStyles = {
    opacity: isDragging ? '0.5' : '1',
    marginRight: '20px',
    ...props.style
  };

  const descriptionStyle = `description-${props.layerId}`;

  const setClickTriggerStr = (str) => props.setParagraphClickTriggerStr(props.layerId, props.id, str);
  if (props.isDragging) {
    console.log("isDragging", props.id)
  }
  
  if (isDragging) {
    return (
      <span
        ref={ref}
        className={descriptionStyle}
        style={inlineStyles}
      >
        <Tag className='description-tag' {...props.attributes} {...props.listeners}>{props.tag[language]}</Tag>
        <Paragraph className='description-paragraph' editable={{onChange: setClickTriggerStr}}>
          {props.text[language]}
        </Paragraph>
      </span>
    );
  } else {
    return (
      <span
        ref={ref}
        className={descriptionStyle}
        style={inlineStyles}
        onMouseEnter={() => {props.setVisualCue(props.id)}}
        onMouseLeave={() => {props.setVisualCue()}}
      >
        <Tag className='description-tag' {...props.attributes} {...props.listeners}>{props.tag[language]}</Tag>
        <Paragraph className='description-paragraph' editable={{onChange: setClickTriggerStr}}>
          {props.text[language]}
        </Paragraph>
      </span>
    );
  }
});

export default function SortableItem(props) {

  const {
    attributes,
    isDragging,
    listeners,
    setNodeRef,
    transform,
    transition
  } = useSortable({id: props.id});
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition: transition
  };

  return (
    <Item
      ref={setNodeRef}
      attributes={attributes}
      isDragging={isDragging}
      listeners={listeners}
      style={style}
      {...props}
    />
  );
};