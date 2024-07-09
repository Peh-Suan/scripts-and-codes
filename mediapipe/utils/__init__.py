import cv2
import mediapipe as mp
import pandas as pd
import datetime
import os
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
import pickle

current_dir = os.path.dirname(os.path.abspath(__file__))

triangles_inner = [(78, 191, 95),
                   (191, 95, 88),
                   (191, 80, 88),
                   (80, 88, 178),
                   (80, 81, 178),
                   (81, 178, 87),
                   (81, 82, 87),
                   (82, 13, 87),
                   (13, 14, 87),
                   (13, 14, 312),
                   (14, 312, 317),
                   (312, 311, 317),
                   (311, 317, 402),
                   (311, 402, 310),
                   (310, 402, 318),
                   (310, 318, 415),
                   (318, 415, 324),
                   (324, 415, 308)]

def distance(point1, point2):
    return sum([(n1 - n2)**2 for n1, n2 in zip(point1, point2)])**.5

def triangle_area(x, y, z):
    s1, s2, s3 = distance(x, y), distance(y, z), distance(x, z)
    s = (s1 + s2 + s3)/2
    area = (s*(s - s1)*(s - s2)*(s - s3))**.5  

    return area

class TraceFace():
    
    def __init__(self, video_path, data_file_name='', data_file_type='csv'):
        assert data_file_type in ["pickle", "csv"]
        self.lips = json.load(open(os.path.join(current_dir, 'lip_landmarks.json')))
        self.lips_all = self.lips['outer']['upper'] + self.lips['outer']['lower'] + self.lips['inner']['upper'] + self.lips['inner']['lower']
        self.video_path = video_path
        self.extension = '.'+self.video_path.split('.')[-1]
        if not data_file_name:
            self.data_file_name = self.video_path.replace(self.extension, '') + f'.{data_file_type}'
        else:
            self.data_file_name = f'{data_file_name}.{data_file_type}'
        
        self._init()
    
    def _init(self):
        self.cap = cv2.VideoCapture(self.video_path)
        self._trace_face(0, draw=False)
        
        self.total_n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
            
        if os.path.isfile(self.data_file_name):
            self._results = self._get_results(from_saved=True)
        
        else:
            self._results = {frame: None for frame in range(self.total_n_frames)}
    
    def _terminate(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def _extract_frame(self, frame_num):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num-1)
        return self.cap.read()

    def _trace_face(self, frame_num, draw):
        
        success, frame = self._extract_frame(frame_num)
        
        if success:
            image = frame
            
            drawingModule = mp.solutions.drawing_utils
            faceModule = mp.solutions.face_mesh

            circleDrawingSpec = drawingModule.DrawingSpec(thickness=1, circle_radius=1, color=(0,255,0))
            lineDrawingSpec = drawingModule.DrawingSpec(thickness=1, color=(0,255,0))

            with faceModule.FaceMesh(static_image_mode=True) as face:
                result = face.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if result.multi_face_landmarks != None:
                    faceRecognized = True
                    
                    if draw:
                        for faceLandmarks in result.multi_face_landmarks:
                            drawingModule.draw_landmarks(image, faceLandmarks, faceModule.FACEMESH_CONTOURS, circleDrawingSpec, lineDrawingSpec)
                
                else:
                    faceRecognized = False
                        
            return success, faceRecognized, image, result
        
        else:
            return success, False, None, None
    
    def trace(self, start_frame=None, end_frame=None, auto_save=True, save_interval=2, only_lips=False):
        if not start_frame: start_frame = 0
        if not end_frame: end_frame = self.total_n_frames

        traced_frames = [frame for frame in self._results if self._results[frame]]
        
        self.last_saved_time = datetime.datetime.now()
            
        for frame_num in tqdm(range(start_frame, end_frame)):
            if frame_num in traced_frames: continue
            
            success, faceRecognized, image, result = self._trace_face(frame_num, draw=False)
                    
            if success and faceRecognized:
                self._results[frame_num] = self._solution_to_dict(result, only_lips)

            if auto_save and (datetime.datetime.now()-self.last_saved_time>=datetime.timedelta(minutes=save_interval)):
                self._save(only_lips)
                self.last_saved_time = datetime.datetime.now()
        
        if auto_save: self._save(only_lips)
    
    def save(self, only_lips):
        self._save(only_lips)
    
    def _solution_to_dict(self, solution, only_lips):
        data = {}
        for landmark_idx, landmark in enumerate(solution.multi_face_landmarks[0].landmark):
            if only_lips and landmark_idx not in self.lips_all: continue
            data[landmark_idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z
            }
        
        return data
    
    def _save(self, only_lips):
        if self.data_file_name.endswith(".pickle"):
            if only_lips:
                results = {frame: {landmark: self._results[frame][landmark] for landmark in self._results[frame] if landmark in self.lips_all} for frame in self._results if self._results[frame]!=None}
            else:
                results = {frame: self._results[frame] for frame in self._results if self._results[frame]!=None}
            with open(self.data_file_name, 'wb') as f:
                pickle.dump(results, f)
        
        elif self.data_file_name.endswith(".csv"):
            self._results_to_dataframe(only_lips=only_lips, from_saved=False, show_progress=False).to_csv(self.data_file_name)

    def _get_results(self, from_saved):
        if from_saved:
            print(f"Exising data file `{self.data_file_name}` found. Using those results.")
            if self.data_file_name.endswith(".pickle"):
                with open(self.data_file_name, 'rb') as f:
                    results = pickle.load(f)
            elif self.data_file_name.endswith(".csv"):
                df = pd.read_csv(self.data_file_name)
                results = {}
                pbar = tqdm(sorted(list(set(df["frame"]))))
                for frame in pbar:
                    this_df = df[df.frame==frame]
                    data = {}
                    landmarks = this_df["landmark"]
                    n_landmarks = len(landmarks)
                    for idx, landmark in enumerate(sorted(list(set(landmarks)))):
                        data[landmark] = {
                            'x': float(this_df[this_df.landmark==landmark].x),
                            'y': float(this_df[this_df.landmark==landmark].y),
                            'z': float(this_df[this_df.landmark==landmark].z),
                        }
                        
                        pbar.set_postfix({"landmark": landmark, "remain": n_landmarks-idx-1})
                    results[frame] = data
            
            return results
        
        return self._results

    def plot(self, frame, draw=False):
        success, faceRecognized, image, result = self._trace_face(frame, draw)
        if success:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(img)
        else:
            print('Extraction failed.')
        
    def get_solution(self, frame):
        success, faceRecognized, image, result = self._trace_face(frame, draw=False)
        return result

    def get_result(self, frame, only_lips=False):
        success, faceRecognized, image, result = self._trace_face(frame, draw=False)
        if not faceRecognized: return None
        
        return self._solution_to_dict(result, only_lips)

    def get_image(self, frame, draw=False):
        success, faceRecognized, image, result = self._trace_face(frame, draw=draw)
        return image
    
    def get_frame_at_time(self, time):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return int(time*fps)
    
    def save_image(self, frame, file_name, draw=False):
        cv2.imwrite(file_name, self.get_image(frame, draw=draw))
    
    def get_results(self, from_saved=True):
        traced_landmarks = {frame: self._results[frame] for frame in self._get_results(from_saved) if self._results[frame]}
        return traced_landmarks
    
    def _results_to_dataframe(self, start_frame=None, end_frame=None, only_lips=False, from_saved=True, show_progress=True):
        if not start_frame: start_frame = 0
        if not end_frame: end_frame = self.total_n_frames
        traced_landmarks = self.get_results(from_saved)
        
        data = {
            'frame': [],
            'landmark': [],
            'x': [],
            'y': [],
            'z': []
        }
        if show_progress:
            pbar = tqdm(traced_landmarks)
        else:
            pbar = traced_landmarks
        for frame in pbar:
            if frame not in range(start_frame, end_frame): continue
            landmarks = traced_landmarks[frame]
            left_landmark = landmarks[78]
            right_landmark = landmarks[308]
            original = (left_landmark['x'] + right_landmark['x'])/2, (left_landmark['y'] + right_landmark['y'])/2, (left_landmark['z'] + right_landmark['z'])/2
            
            for landmark_idx in landmarks:
                landmark = landmarks[landmark_idx]
                if (not only_lips) or (landmark_idx in self.lips_all):
                    x, y, z = landmark['x'] - original[0], landmark['y'] - original[1], landmark['z'] - original[2]
                    
                    data['frame']+=[frame]
                    data['landmark']+=[landmark_idx]
                    data['x']+=[x]
                    data['y']+=[y]
                    data['z']+=[z]

        return pd.DataFrame(data)
        
    def results_to_dataframe(self, start_frame=None, end_frame=None, only_lips=False):
        return self._results_to_dataframe(start_frame=start_frame, end_frame=end_frame, only_lips=only_lips, from_saved=True)

