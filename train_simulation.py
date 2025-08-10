import threading
import time
import random
import sqlite3
from flask_socketio import emit
from dataclasses import dataclass
from typing import List, Dict, Tuple
import logging

@dataclass
class Train:
    id: int
    line: str  # 'LRT' or 'MRT'
    direction: str  # 'Gombak' or 'Putra Heights' for LRT; 'Sungai Buloh' or 'Kajang' for MRT
    current_station_id: int
    next_station_id: int
    arrival_time: float
    route_stations: List[int]
    current_route_index: int

class TrainSimulation:
    def __init__(self, socketio):
        self.socketio = socketio
        self.trains = {}
        self.running = False
        self.simulation_thread = None
        
        # Define station routes
        self.lrt_stations = self._get_lrt_stations()  # Gombak to Putra Heights
        self.mrt_stations = self._get_mrt_stations()  # Sungai Buloh to Kajang
        
        self.logger = logging.getLogger(__name__)
        
    def _get_lrt_stations(self) -> List[int]:
        """Get LRT station IDs in order from Gombak to Putra Heights"""
        conn = sqlite3.connect('metro.db')
        c = conn.cursor()
        
        # LRT stations in order (based on the route data)
        lrt_station_names = [
            "Gombak", "Taman Melati", "Wangsa Maju", "Sri Rampai", "Setiawangsa",
            "Jelatek", "Dato' Keramat", "Damai", "Ampang Park", "KLCC", "Kampung Baru",
            "Dang Wangi", "Masjid Jamek (KJL)", "Pasar Seni (KJL)", "KL Sentral (KJL)",
            "Bangsar", "Abdullah Hukum", "Kerinchi", "Universiti", "Taman Jaya",
            "Asia Jaya", "Taman Paramount", "Taman Bahagia", "Kelana Jaya",
            "Lembah Subang", "Ara Damansara", "Glenmarie", "Subang Jaya",
            "SS 15", "SS 18", "USJ 7 (KJL)", "Taipan", "Wawasan", "USJ 21",
            "Alam Megah", "Subang Alam", "Putra Heights (KJL)"
        ]
        
        station_ids = []
        for name in lrt_station_names:
            c.execute("SELECT station_id FROM stations WHERE name=?", (name,))
            result = c.fetchone()
            if result:
                station_ids.append(result[0])
        
        conn.close()
        return station_ids
    
    def _get_mrt_stations(self) -> List[int]:
        """Get MRT station IDs in order from Sungai Buloh to Kajang"""
        conn = sqlite3.connect('metro.db')
        c = conn.cursor()
        
        # MRT stations in order
        mrt_station_names = [
            "Sungai Buloh", "Kampung Selamat", "Kwasa Damansara", "Kwasa Sentral",
            "Kota Damansara", "Surian", "Mutiara Damansara", "Bandar Utama",
            "TTDI", "Phileo Damansara", "Pusat Bandar Damansara", "Semantan",
            "Muzium Negara", "Pasar Seni (SBK)", "Merdeka", "Bukit Bintang",
            "Tun Razak Exchange (TRX)", "Cochrane", "Maluri (SBK)",
            "Taman Pertama", "Taman Midah", "Taman Mutiara", "Taman Connaught",
            "Taman Suntex", "Sri Raya", "Bandar Tun Hussein Onn",
            "Batu 11 Cheras", "Bukit Dukung", "Sungai Jernih", "Stadium Kajang", "Kajang"
        ]
        
        station_ids = []
        for name in mrt_station_names:
            c.execute("SELECT station_id FROM stations WHERE name=?", (name,))
            result = c.fetchone()
            if result:
                station_ids.append(result[0])
        
        conn.close()
        return station_ids
    
    def _create_trains(self):
        """Create trains for both LRT and MRT lines"""
        train_id = 1
        
        # Create 44 LRT trains (22 in each direction)
        for i in range(44):
            direction = "Putra Heights" if i % 2 == 0 else "Gombak"
            route_stations = self.lrt_stations if direction == "Putra Heights" else list(reversed(self.lrt_stations))
            
            # Better distribution - spread trains more evenly across the route
            total_stations = len(route_stations)
            station_index = (i * 3) % total_stations  # More spacing between trains
            current_station = route_stations[station_index]
            next_station_index = (station_index + 1) % total_stations
            next_station = route_stations[next_station_index]
            
            # Set more realistic arrival times - trains should arrive every 2-8 minutes for LRT
            arrival_offset = random.randint(30, 480)  # 30 seconds to 8 minutes
            
            train = Train(
                id=train_id,
                line='LRT',
                direction=direction,
                current_station_id=current_station,
                next_station_id=next_station,
                arrival_time=time.time() + arrival_offset,
                route_stations=route_stations,
                current_route_index=station_index
            )
            
            self.trains[train_id] = train
            print(f"Created LRT train {train_id} to {direction}, arrives in {arrival_offset} seconds")
            train_id += 1
        
        # Create 56 MRT trains (28 in each direction)
        for i in range(56):
            direction = "Kajang" if i % 2 == 0 else "Sungai Buloh"
            route_stations = self.mrt_stations if direction == "Kajang" else list(reversed(self.mrt_stations))
            
            # Better distribution - spread trains more evenly across the route
            total_stations = len(route_stations)
            station_index = (i * 2) % total_stations  # More spacing between trains
            current_station = route_stations[station_index]
            next_station_index = (station_index + 1) % total_stations
            next_station = route_stations[next_station_index]
            
            # Set more realistic arrival times - trains should arrive every 2-8 minutes for MRT
            arrival_offset = random.randint(30, 480)  # 30 seconds to 8 minutes
            
            train = Train(
                id=train_id,
                line='MRT',
                direction=direction,
                current_station_id=current_station,
                next_station_id=next_station,
                arrival_time=time.time() + arrival_offset,
                route_stations=route_stations,
                current_route_index=station_index
            )
            
            self.trains[train_id] = train
            print(f"Created MRT train {train_id} to {direction}, arrives in {arrival_offset} seconds")
            train_id += 1
    
    def _move_train(self, train: Train):
        """Move a train to the next station"""
        # Move to next station
        train.current_station_id = train.next_station_id
        train.current_route_index = (train.current_route_index + 1) % len(train.route_stations)
        
        # Set next station
        next_index = (train.current_route_index + 1) % len(train.route_stations)
        train.next_station_id = train.route_stations[next_index]
        
        # Add realistic station delay (10-20 seconds for doors, passengers)
        station_delay = random.randint(10, 20)
        
        # Set new arrival time (60-120 seconds travel time + station delay)
        travel_time = random.randint(60, 120)
        train.arrival_time = time.time() + travel_time + station_delay
        
        print(f"Train {train.id} ({train.line} to {train.direction}) moved to station {train.current_station_id}, next arrival in {travel_time + station_delay}s")
    
    def _update_arrivals_table(self):
        """Update the arrivals table with real train positions and arrival times"""
        conn = sqlite3.connect('metro.db')
        c = conn.cursor()
        
        # Clear existing arrivals
        c.execute("DELETE FROM arrivals")
        
        # Get all stations
        c.execute("SELECT station_id, name FROM stations")
        stations = c.fetchall()
        
        current_time = time.time()
        
        for station_id, station_name in stations:
            # Find all trains that will arrive at this station and group by direction
            arrivals_by_direction = {}
            
            for train_id, train in self.trains.items():
                arrival_time = self._calculate_train_arrival_time(train, station_id, current_time)
                
                # Only include future arrivals (trains that haven't arrived yet)
                if arrival_time > current_time + 5:  # At least 5 seconds in future
                    direction = train.direction
                    
                    if direction not in arrivals_by_direction:
                        arrivals_by_direction[direction] = []
                    
                    arrivals_by_direction[direction].append({
                        'train_id': train_id,
                        'arrival_time': arrival_time,
                        'direction': direction
                    })
            
            # Sort each direction by arrival time and take next 3
            for direction, trains in arrivals_by_direction.items():
                trains.sort(key=lambda x: x['arrival_time'])
                next_3_trains = trains[:3]
                
                for train_info in next_3_trains:
                    # Get destination station ID based on direction
                    dest_station_id = self._get_destination_station_id(direction)
                    
                    # Insert real train arrival
                    c.execute(
                        "INSERT INTO arrivals (station_id, train_id, destination_id, arrival_timestamp) VALUES (?, ?, ?, ?)",
                        (station_id, train_info['train_id'], dest_station_id, train_info['arrival_time'])
                    )
        
        conn.commit()
        conn.close()
        
        # Emit socket event to notify clients
        if hasattr(self, 'socketio') and self.socketio:
            self.socketio.emit('train_update', {'timestamp': current_time})
        
        trains_moved = sum(1 for train in self.trains.values() if train.arrival_time <= current_time)
        print(f"Updated arrivals table at {time.strftime('%H:%M:%S')} - Real train positions calculated")
    
    def _calculate_train_arrival_time(self, train, target_station_id, current_time):
        """Calculate when a train will actually arrive at a target station"""
        # If train is already at or past the target station, calculate next loop arrival
        route = train.route_stations
        current_index = train.current_route_index
        
        # Find target station in the route
        try:
            target_index = route.index(target_station_id)
        except ValueError:
            # Station not in this train's route, return very far future time
            return current_time + 86400  # 24 hours in future
        
        # Calculate stations between current position and target
        if target_index >= current_index:
            # Target is ahead in current loop
            stations_to_target = target_index - current_index
        else:
            # Target is in next loop (train needs to complete current route first)
            stations_to_target = (len(route) - current_index) + target_index
        
        # Calculate arrival time based on:
        # 1. Current train's next arrival time (when it reaches next_station_id)
        # 2. Time to travel from next station to target station
        if stations_to_target == 0:
            # Train is already at the target station, return small delay for departure
            return current_time + 30  # 30 seconds for departure
        elif stations_to_target == 1:
            # Target is the very next station
            return train.arrival_time
        else:
            # Add travel time for additional stations
            # Each station takes 60-120 seconds travel time + 10-20 seconds station delay
            additional_travel_time = (stations_to_target - 1) * 90  # Average 90 seconds per station
            return train.arrival_time + additional_travel_time
    def _get_destination_station_id(self, direction):
        """Get the destination station ID based on direction"""
        if direction == 'Gombak':
            return 1  # Gombak station ID
        elif direction == 'Putra Heights':
            return 37  # Putra Heights station ID  
        elif direction == 'Sungai Buloh':
            return 38  # Sungai Buloh station ID
        elif direction == 'Kajang':
            return 68  # Kajang station ID
        else:
            return 1  # Default fallback
    
    def _simulation_loop(self):
        """Main simulation loop with real train tracking"""
        update_counter = 0
        
        while self.running:
            current_time = time.time()
            trains_moved = 0
            trains_ready_to_move = 0
            
            # Check and move trains that have arrived at their next station
            for train in list(self.trains.values()):
                if current_time >= train.arrival_time:
                    trains_ready_to_move += 1
                    self._move_train(train)
                    trains_moved += 1
            
            # Update arrivals table with real train positions every 2 seconds
            if update_counter % 2 == 0:
                self._update_arrivals_table()
            
            # Debug info every 20 seconds
            if update_counter % 20 == 0:
                next_arrival_times = [int((train.arrival_time - current_time) / 60) for train in list(self.trains.values())[:5]]
                print(f"Debug: {trains_ready_to_move} trains ready, next arrivals in: {next_arrival_times} minutes")
            
            update_counter += 1
            time.sleep(1)  # Update every second for real-time accuracy
            
            # Update arrivals table every 2 seconds for more responsive updates
            update_counter += 1
            if update_counter % 2 == 0:  # Every 2 seconds instead of 5
                self._update_arrivals_table()
                print(f"Updated arrivals table at {time.strftime('%H:%M:%S')} - {trains_moved} trains moved this cycle")
                if update_counter >= 40:  # Reset counter every 40 cycles
                    update_counter = 0
            
            time.sleep(1)  # Update every second
    
    def start(self):
        """Start the train simulation"""
        if not self.running:
            self.running = True
            print("Creating trains...")
            print(f"LRT stations loaded: {len(self.lrt_stations)} stations")
            print(f"MRT stations loaded: {len(self.mrt_stations)} stations")
            
            if len(self.lrt_stations) == 0 or len(self.mrt_stations) == 0:
                print("ERROR: No stations loaded! Check database connection.")
                return
            
            self._create_trains()
            print(f"Created {len(self.trains)} trains total")
            print("Updating initial arrivals table...")
            self._update_arrivals_table()  # Initial update
            print("Starting simulation thread...")
            self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.simulation_thread.start()
            print("Train simulation started successfully!")
            self.logger.info("Train simulation started")
    
    def stop(self):
        """Stop the train simulation"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join()
        self.logger.info("Train simulation stopped")

# Global simulation instance
simulation = None

def init_train_simulation(socketio):
    """Initialize the train simulation"""
    global simulation
    simulation = TrainSimulation(socketio)
    simulation.start()
    return simulation

def get_simulation():
    """Get the global simulation instance"""
    return simulation