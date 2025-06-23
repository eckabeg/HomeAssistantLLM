import './App.css';
import FloorPlan from "./components/Floor"
import Thermostat from "./components/Thermostat";

function App() {
    return (
        <div className="App h-screen w-screen">
            <Thermostat/>
            <FloorPlan/>
        </div>
    );
}

export default App;