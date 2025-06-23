import {useEffect, useState} from "react";

export default function Thermostat() {

    const [thermostatLivingRoom, setThermostatLivingRoom] = useState(21)
    const [thermostatBath, setThermostatBath] = useState(21)
    const [thermostatKitchen, setThermostatKitchen] = useState(21)
    const [thermostatFloor, setThermostatFloor] = useState(21)

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:9090');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'SET_TEMPERATURE') {
                if (data.payload.value.entity_id.includes("living_room")) {
                    setThermostatLivingRoom(data.payload.value.temperature)
                }
            }
        };

        return () => ws.close();
    }, []);

    return (
        <div>
            <div>
                <p>Thermostat Living Room</p>
                <p>{thermostatLivingRoom}</p>
            </div>

            <div>
                <p>Thermostat Bath</p>
                <p>{thermostatBath}</p>
            </div>

            <div>
                <p>Thermostat Kitchen</p>
                <p>{thermostatKitchen}</p>
            </div>

            <div>
                <p>Thermostat Floor</p>
                <p>{thermostatFloor}</p>
            </div>
        </div>
    )
}