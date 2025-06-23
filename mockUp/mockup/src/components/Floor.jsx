import React, { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrthographicCamera, Stats, SoftShadows, OrbitControls } from "@react-three/drei";
import { ReadCSVData, Wall } from "./Walls";

const WARM = [213,66,37]
const COLD = [37, 162, 213]

export default function FloorPlan() {

    const [walls, setWalls] = useState([]);
    const [temperature, setTemperature] = useState(`rgb(${COLD[0]}, ${COLD[1]}, ${COLD[2]})`)
    const [livingRoomIntensity, setLivingRoomIntensity] = useState(0)
    const [kitchenIntensity, setKitchenIntensity] = useState(0)
    const [hallwayIntensity, setHallwayIntensity] = useState(0)
    const [bathIntensity, setBathIntensity] = useState(0)

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:9090');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'TURN_ON') {
                if (data.payload.value.entity_id.includes("living_room")) {
                    setIntensity(setLivingRoomIntensity)
                } else if (data.payload.value.entity_id.includes("kitchen")) {
                    setIntensity(setKitchenIntensity)
                } else if (data.payload.value.entity_id.includes("hallway")) {
                    setIntensity(setHallwayIntensity)
                } else if (data.payload.value.entity_id.includes("bath")) {
                    setIntensity(setBathIntensity)
                }
            }

            if (data.type === 'TURN_OFF') {
                if (data.payload.value.entity_id.includes("living_room")) {
                    setIntensity(setLivingRoomIntensity)
                } else if (data.payload.value.entity_id.includes("kitchen")) {
                    setIntensity(setKitchenIntensity)
                } else if (data.payload.value.entity_id.includes("hallway")) {
                    setIntensity(setHallwayIntensity)
                } else if (data.payload.value.entity_id.includes("bath")) {
                    setIntensity(setBathIntensity)
                }
            }

            if (data.type === 'SET_TEMPERATURE') {

            }
        };

        return () => ws.close();
    }, []);

    useEffect(() => {
        async function loadWalls() {
            try {
                ReadCSVData("walls.csv")
                    .then((data) => {
                        const wallData = data;
                        setWalls(wallData);
                    })
            } catch (error) {
                console.error("Error loading walls:", error);
            }
        }
        loadWalls();
    }, []);

    const setIntensity = (setFunc) => {
        setFunc(prev => Math.abs(1 - prev));
    }
    const handleTemperatureChange = (e) => {
        var t = e.target.value / 100
        const lerp = (n, x) => {
            return Math.round(n + (x - n) * t)
        }
        let r = lerp(COLD[0], WARM[0]);
        let g = lerp(COLD[1], WARM[1]);
        let b = lerp(COLD[2], WARM[2]);
        let c = `rgb(${r},${g},${b})`;
        setTemperature(c);
    }

    return (
        <div>
            <div>
                <button onClick={() => setIntensity(setLivingRoomIntensity)} className="Light-Button">
                    Living Room
                </button>
                <button onClick={()=>setIntensity(setBathIntensity)} className="Light-Button">Toilet</button>
                <button onClick={()=>setIntensity(setHallwayIntensity)} className="Light-Button">Hallway</button>
                <button onClick={()=>setIntensity(setKitchenIntensity)} className="Light-Button">Kitchen</button>
                <input type="range" onChange={handleTemperatureChange}/>
            </div>
            <Canvas shadows style={{ width: '100vw', height: '80vh' }}>
                <OrthographicCamera
                    makeDefault
                    position={[0, 15, 0]}
                    zoom={20}
                    near={0.1}
                    far={100}
                />

                <OrbitControls
                    enablePan={false}
                    enableZoom={true}
                    enableRotate={true}
                />

                {/* Lighting */}
                <ambientLight intensity={1} color={temperature} />

                <rectAreaLight
                    position={[0,0.1,15]}
                    width={30}
                    height={20}
                    intensity={kitchenIntensity}
                    rotation={[-Math.PI / 2, 0, 0]}
                    color="#ff6beb"
                />
                <rectAreaLight
                    position={[0,0.1,-15]}
                    width={30}
                    height={20}
                    intensity={livingRoomIntensity}
                    rotation={[-Math.PI / 2, 0, 0]}
                    color="#ff6beb"
                />
                <rectAreaLight
                    position={[7,0.1,0]}
                    width={5}
                    height={10}
                    intensity={bathIntensity}
                    rotation={[-Math.PI / 2, 0, 0]}
                    color="#ff6beb"
                />
                <rectAreaLight
                    position={[1,0.1,0]}
                    width={5}
                    height={10}
                    intensity={hallwayIntensity}
                    rotation={[-Math.PI / 2, 0, 0]}
                    color="#ff6beb"
                />
                <rectAreaLight
                    position={[-5,0.1,-4]}
                    width={18}
                    height={2.5}
                    intensity={hallwayIntensity}
                    rotation={[-Math.PI / 2, 0, 0]}
                    color="#ff6beb"
                />

                <SoftShadows size={10} samples={30} focus={0.5} />

                {/* Floor */}
                <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
                    <planeGeometry args={[20, 30]} />
                    <meshStandardMaterial color="lightgray" />
                </mesh>
                <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[-6, 3, 1]}>
                    <planeGeometry args={[8,8]} />
                    <meshStandardMaterial color="black" />
                </mesh>

                {/* walls */}
                {Array.isArray(walls) && walls.length > 0 && walls.map((wall, index) => (
                    <Wall
                        key={index}
                        x={wall.x}
                        y={wall.y}
                        length={wall.length}
                        rotation={wall.rotation}
                    />
                ))}

                <Stats />
            </Canvas>
        </div>
    );
}
