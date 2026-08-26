import '../dashboard/dashboard.css';

const cases = [
  ['FASAL-10482', 'Soybean', 'Soybean rust', '87%', 'Moderate'],
  ['FASAL-10479', 'Soybean', 'Bacterial blight', '74%', 'Early'],
  ['FASAL-10471', 'Soybean', 'Uncertain', '48%', 'Review'],
];

export default function AgronomistPage() {
  return <main className="dashboard"><header className="dash-head"><div className="brand"><span className="mark">R</span>RAKSHAK AI</div><div className="user">AGRONOMIST <span>AG</span></div></header><section className="dash-wrap"><div className="dash-intro"><div><p className="eyebrow">EXPERT REVIEW QUEUE</p><h1>Make every signal useful.</h1></div><button className="button">Refresh queue <span>↻</span></button></div><section className="table-panel"><div className="panel-heading"><h2>Cases awaiting verification</h2><span>{cases.length} open cases</span></div><div className="farm-row header"><span>Case</span><span>Crop</span><span>AI indication</span><span>Confidence</span></div>{cases.map(row => <div className="farm-row" key={row[0]}><span>{row[0]}</span><span>{row[1]}</span><span>{row[2]}</span><span className="severity">{row[3]} · {row[4]}</span></div>)}</section></section></main>;
}

