// Fixed, public official weather endpoints. No user-supplied upstream URLs.
const IPMA="https://api.ipma.pt/open-data/";
const headers={"Cache-Control":"public, max-age=300, s-maxage=600","Content-Type":"application/json; charset=utf-8"};
async function get(url){const r=await fetch(url,{headers:{"User-Agent":"VelvetVerseRadio-weather/1.0"},signal:AbortSignal.timeout(10000)});if(!r.ok)throw new Error("Upstream "+r.status);return r}
async function toronto(){
 const now=new Date();
 for(let back=0;back<5;back++){
  const d=new Date(now.getTime()-back*3600000),day=d.toISOString().slice(0,10).replace(/-/g,""),hour=String(d.getUTCHours()).padStart(2,"0");
  const base="https://dd.weather.gc.ca/"+(back===0?"today":day)+"/citypage_weather/ON/"+hour+"/";
  try{const listing=await (await get(base)).text();const files=[...listing.matchAll(/(\d{8}T\d{6}\.\d+Z_MSC_CitypageWeather_s0000458_en\.xml)/g)].map(m=>m[1]).sort().reverse();if(files.length){const xml=await(await get(base+files[0])).text();if(xml.includes("<siteData"))return xml}}catch(e){}
 }
 throw new Error("Toronto official feed unavailable");
}
export async function onRequestGet({request}){
 const kind=new URL(request.url).searchParams.get("kind");
 try{
  if(kind==="toronto")return new Response(JSON.stringify({xml:await toronto()}),{headers});
  if(kind==="portugal"){
   const ids=[1110600,1131200,1080500];
   const [obs,...forecasts]=await Promise.all([get(IPMA+"observation/meteorology/stations/obs-surface.geojson").then(r=>r.json()),...ids.map(id=>get(IPMA+"forecast/meteorology/cities/daily/"+id+".json").then(r=>r.json()))]);
   const stations=[1200535,1200545,1200554];
   const cities=ids.map((id,i)=>({id,observations:obs.features.filter(f=>f.properties.idEstacao===stations[i]).map(f=>f.properties).sort((a,b)=>b.time.localeCompare(a.time)),forecast:forecasts[i]}));
   return new Response(JSON.stringify({cities}),{headers});
  }
  return new Response(JSON.stringify({error:"Unknown weather region"}),{status:400,headers:{"Content-Type":"application/json"}});
 }catch(e){return new Response(JSON.stringify({error:"Official weather data temporarily unavailable"}),{status:503,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}})}
}
