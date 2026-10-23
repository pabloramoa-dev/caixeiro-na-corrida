/**
 * Pós-produção Remotion sobre o MP4 REAL produzido pelo motor
 * Manim + HyperFrames, mantendo voz original e sincronização labial.
 * TODOS os efeitos são determinísticos por frame; nenhum componente
 * cobre o rosto, as legendas nem o bloco de informações existente.
 */
import React from 'react';
import {
  AbsoluteFill, OffthreadVideo, Easing, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';

export const PREVIEW_FRAMES = 960; // 32s, vertical 1080x1920, 30fps
const marks = [3.9, 8.2, 13.2, 18.6, 24.4, 28.7]; // marcos experimentais
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const pulse = (t:number, center:number, spread=0.32) => {
  const delta = Math.abs(t-center);
  return Math.max(0, 1-delta/spread);
};
const getPulse = (sec:number) => Math.max(...marks.map((mark) => pulse(sec, mark)));
const clamp01 = (n:number) => Math.min(1,Math.max(0,n));

export const CaixeiroCinema: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sec = frame/fps;
  const hit = getPulse(sec);
  const opening = spring({fps, frame, config:{damping:200, stiffness:80}});
  const endFade = interpolate(frame,[PREVIEW_FRAMES-24,PREVIEW_FRAMES-1],[1,0],clamp);
  const introFade = interpolate(frame,[0,14],[0,1],clamp);
  const opacity = Math.min(introFade,endFade);
  // Zoom respirando, leve pan de câmera e tremor SOMENTE nos impactos.
  const cameraScale = 1.022 + 0.014*Math.sin(sec*0.32) + 0.023*hit;
  const panX = Math.sin(sec*0.41)*5 + Math.sin(sec*23)*hit*5;
  const panY = Math.sin(sec*0.24)*7 + Math.cos(sec*26)*hit*3;
  const tilt = 0.13*Math.sin(sec*.42) + Math.sin(sec*20)*hit*.18;
  const glowStrength = 0.06 + 0.09*(0.5+0.5*Math.sin(sec*1.1));
  const sweepX = interpolate((frame%210),[0,209],[-1400,1500],clamp);
  const storyProgress = clamp01(frame/(PREVIEW_FRAMES-1));
  const fadeIn = Easing.out(Easing.cubic)(clamp01(sec/1.2));

  return (
    <AbsoluteFill style={{backgroundColor:'#090f21',overflow:'hidden',fontFamily:'Arial, sans-serif'}}>
      <AbsoluteFill style={{
        opacity, transform:`translate(${panX}px,${panY}px) rotate(${tilt}deg) scale(${cameraScale})`,
        transformOrigin:'50% 49%',
      }}>
        <OffthreadVideo
          src={staticFile('source.mp4')}
          durationInFrames={PREVIEW_FRAMES}
          volume={1}
          style={{width:'100%',height:'100%',objectFit:'cover',
            filter:'contrast(1.045) saturate(1.10) brightness(1.018)'}}
        />
      </AbsoluteFill>

      {/* Vinheta e gradação de cor; transparência total sobre as legendas. */}
      <AbsoluteFill style={{pointerEvents:'none',
        background:'radial-gradient(ellipse at 49% 46%, transparent 39%, rgba(7,12,28,0.05) 65%, rgba(7,12,28,0.30) 100%)'}}/>
      <AbsoluteFill style={{pointerEvents:'none',mixBlendMode:'screen', opacity:glowStrength*opening,
        background:'linear-gradient(128deg, rgba(251,182,91,.22) 0%, transparent 31%, transparent 80%)'}}/>

      {/* Feixes luminosos de passagem: sem placas de texto sobre o personagem. */}
      <AbsoluteFill style={{pointerEvents:'none',mixBlendMode:'screen',opacity:0.075*fadeIn,
        transform:`translateX(${sweepX}px) rotate(20deg)`,
        background:'linear-gradient(90deg, transparent 35%, rgba(255,211,124,.7) 49%,transparent 64%)'}}/>

      {/* Micro-impacto de luz, limitado para evitar flash agressivo. */}
      <AbsoluteFill style={{pointerEvents:'none',opacity:0.12*hit,
        backgroundColor:'#ffdfb5'}}/>

      {/* Reflexos/bokeh nos cantos, animados de modo determinístico. */}
      {[0,1,2,3,4,5].map(i=>{
        const x = i%2===0 ? -45+(i*31) : 960-(i*12);
        const y = 340+i*248 + Math.sin(sec*(.43+i*.08))*14;
        const size = 24+(i%3)*15;
        return <div key={i} style={{position:'absolute',left:x,top:y,width:size,height:size,
          borderRadius:'100%',filter:'blur(12px)',pointerEvents:'none',mixBlendMode:'screen',
          opacity:0.08+0.03*Math.sin(sec*.7+i),
          background:i%2 ? '#ffd49b':'#8ed6ff'}}/>;
      })}

      {/* Indicador editorial DISCRETO, sem tarja grande fixa. */}
      <div style={{position:'absolute',top:112,right:42,display:'flex',
        alignItems:'center',gap:9,opacity:0.65*opening,letterSpacing:3,
        fontSize:17,fontWeight:700,color:'#fff',
        textShadow:'0 1px 8px #071322'}}>
        <div style={{width:7,height:7,background:'#ffb84d',borderRadius:'50%',
          boxShadow:'0 0 10px #ffb84d'}}/>
        REMOTION · TESTE
      </div>
      {/* Risco de progresso lateral, não disputa espaço com as legendas originais. */}
      <div style={{position:'absolute',left:11,top:300,bottom:300,width:3,
        background:'rgba(255,255,255,.10)',borderRadius:4,pointerEvents:'none'}}>
        <div style={{width:'100%',height:`${100*storyProgress}%`,
          background:'linear-gradient(#ffd78c,#f2a748)',boxShadow:'0 0 6px #f6ae4a',
          borderRadius:4}}/>
      </div>
      {/* Saída final suave; conteúdo e áudio originais preservados. */}
      <AbsoluteFill style={{pointerEvents:'none',
        background:'#090f21',
        opacity:1-endFade}}/>
    </AbsoluteFill>
  );
};
