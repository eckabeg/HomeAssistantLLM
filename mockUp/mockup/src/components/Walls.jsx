import Papa from "papaparse";
// I need a function that reads in a json file.



export function Wall({ x, y, length, rotation }) {
    const rotationRad = (rotation * Math.PI) / 180;
    return (
        <mesh
            position={[x, 1.5, y]}
            rotation={[0, rotationRad, 0]}
            castShadow
            receiveShadow
        >
            <boxGeometry args={[length, 3, 0.2]} />
            <meshStandardMaterial color="#8B4513" />
        </mesh>
    );
}

export async function ReadCSVData(path){
    const response = await fetch(path);
    const csv = await response.text();

    const result = Papa.parse(csv, {header:false, dynamicTyping: true, skipEmptyLines: true});
    const walls = result.data.map(row => ({
        x: parseFloat(row[0]) || 0,
        y: parseFloat(row[1]) || 0,
        length: parseFloat(row[2]) || 1,
        rotation: parseFloat(row[3]) || 0
    }));
    console.log(walls)
    return walls;
}
