from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from model_loader import load_generator_model

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL if you want to restrict it
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Sensors(BaseModel):
    part: float
    extract_tank_level: float
    ffte_discharge_density: float
    ffte_discharge_solids: float
    ffte_feed_flow_rate_pv: float
    ffte_feed_solids_pv: float
    ffte_heat_temperature_1: float
    ffte_heat_temperature_2: float
    ffte_heat_temperature_3: float
    ffte_production_solids_pv: float
    ffte_steam_pressure_pv: float
    tfe_input_flow_pv: float
    tfe_level: float
    tfe_motor_current: float
    tfe_motor_speed: float
    tfe_out_flow_pv: float
    tfe_production_solids_pv: float
    tfe_production_solids_density: float
    tfe_steam_pressure_pv: float
    tfe_steam_temperature: float
    tfe_tank_level: float
    tfe_temperature: float
    tfe_vacuum_pressure_pv: float

LATENT_DIM = 8
generator_model = load_generator_model()

# 🔥 WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive JSON data from client
            data = await websocket.receive_json()
            sensors = Sensors(**data)

            # Convert to scaled numpy array
            input_values = [value / 100.0 for value in sensors.dict().values()]
            sensors_array = np.array(input_values).reshape(1, -1).astype(np.float32)

            noise = np.random.normal(0, 1, (1, LATENT_DIM)).astype(np.float32)
            predicted_settings = generator_model.predict([noise, sensors_array])

            settings_list = predicted_settings[0].tolist()

            setting_names = [
                'part' / 100,
                'extract_tank_level' / 100,
                'ffte_discharge_density' / 100,
                'ffte_discharge_solids' / 100,
                'ffte_feed_flow_rate_pv' / 100,
                'ffte_feed_solids_pv' / 100,
                'ffte_heat_temperature_1' / 100,
                'ffte_heat_temperature_2' / 100,
                'ffte_heat_temperature_3' / 100,
                'ffte_production_solids_pv' / 100,
                'ffte_steam_pressure_pv' / 100,
                'tfe_input_flow_pv' / 100,
                'tfe_level' / 100,
                'tfe_motor_current' / 100,
                'tfe_motor_speed' / 100,
                'tfe_out_flow_pv' / 100,
                'tfe_production_solids_pv' / 100,
                'tfe_production_solids_density' / 100,
                'tfe_steam_pressure_pv' / 100,
                'tfe_steam_temperature' / 100,
                'tfe_tank_level' / 100,
                'tfe_temperature' / 100,
                'tfe_vacuum_pressure_pv' / 100,
            ]

            labeled_settings = {name: round(val * 100, 0) for name, val in zip(setting_names, settings_list)}

            await websocket.send_json({
                "recommended_settings": labeled_settings,
                "raw_values": settings_list,
            })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.close(code=1011)
        print(f"WebSocket error: {str(e)}")
