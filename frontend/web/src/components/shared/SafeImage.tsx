import React, { useState } from 'react';

type SafeImageProps = React.ImgHTMLAttributes<HTMLImageElement> & { fallbackSrc?: string };

export const SafeImage: React.FC<SafeImageProps> = ({ fallbackSrc = '/rakshak-leaf.svg', onError, ...props }) => {
  const [src, setSrc] = useState(props.src);
  return <img {...props} src={src || fallbackSrc} onError={(event) => { if (src !== fallbackSrc) setSrc(fallbackSrc); onError?.(event); }} />;
};
