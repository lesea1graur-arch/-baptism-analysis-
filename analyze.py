#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baptism Analysis Tool
Извлечение ключевых кадров и генерация HTML-отчёта православного обряда крещения.
"""

import cv2
import numpy as np
import os
import json
import argparse
from typing import List, Dict


class BaptismAnalyzer:
    """Анализатор видеозаписи таинства крещения."""
    
    def __init__(self, video_path: str, output_dir: str = "./report"):
        self.video_path = video_path
        self.output_dir = output_dir
        self.frames_dir = os.path.join(output_dir, "frames")
        
        os.makedirs(self.frames_dir, exist_ok=True)
        
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        
    def extract_frame(self, timestamp: float) -> np.ndarray:
        """Извлекает кадр на указанной временной метке (в секундах)."""
        frame_num = int(timestamp * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError(f"Не удалось извлечь кадр на {timestamp}s")
        return frame
    
    def save_frame(self, frame: np.ndarray, filename: str) -> str:
        """Сохраняет кадр в файл."""
        path = os.path.join(self.frames_dir, filename)
        cv2.imwrite(path, frame)
        return path
    
    def analyze(self, stages: List[Dict]) -> Dict:
        """Выполняет полный анализ видео по заданным этапам."""
        results = []
        
        print(f"Анализ видео: {self.duration:.1f}s @ {self.fps:.1f} FPS")
        print("-" * 50)
        
        for i, stage in enumerate(stages, 1):
            ts = stage["time"]
            try:
                frame = self.extract_frame(ts)
                fname = f"frame_{ts:.1f}s.jpg"
                self.save_frame(frame, fname)
                
                results.append({
                    **stage,
                    "frame_file": fname,
                    "timestamp": ts,
                    "index": i
                })
                print(f"[{i}/{len(stages)}] {stage['label']} @ {ts:.1f}s")
            except Exception as e:
                print(f"Ошибка на этапе {i}: {e}")
        
        return {
            "video_duration": self.duration,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "stages": results
        }
    
    def release(self):
        """Освобождает ресурсы видео."""
        self.cap.release()


def main():
    parser = argparse.ArgumentParser(description="Анализ обряда крещения")
    parser.add_argument("--video", required=True, help="Путь к видеофайлу")
    parser.add_argument("--output", default="./report", help="Директория для отчёта")
    args = parser.parse_args()
    
    stages = [
        {"time": 0.5, "label": "Подготовка к обряду", 
         "desc": "Священник даёт наставления у купели"},
        {"time": 3.0, "label": "Первое погружение", 
         "desc": "Крещаемый наклоняется над купелью"},
        {"time": 8.0, "label": "Молитва над водой", 
         "desc": "Священник совершает молитву, крещаемый погружён"},
        {"time": 15.0, "label": "Третье погружение", 
         "desc": "Полное троекратное погружение в купель"},
        {"time": 24.0, "label": "Восхождение из воды", 
         "desc": "Крещаемый поднимается, обряд завершён"},
        {"time": 28.5, "label": "Венчание полотенцем", 
         "desc": "Вытирание священным полотенцем"},
    ]
    
    analyzer = BaptismAnalyzer(args.video, args.output)
    data = analyzer.analyze(stages)
    analyzer.release()
    
    with open(os.path.join(args.output, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("-" * 50)
    print(f"Анализ завершён! Кадров извлечено: {len(data['stages'])}")


if __name__ == "__main__":
    main()
