#!/usr/bin/env python3
# Author: Ilayda Ismailoglu
# Date: 2026-03-12
# Description: YOLOv8 quantization config for STM32N6 deployment
"""
ST Object Detection Pipeline
=============================
Bu script tüm adımları sırayla çalıştırır:
1. YOLOv8 model export (TFLite INT8)
2. TFLite Quantization
3. STM32N6 Deployment
"""

import subprocess
import sys
import os         

# Proje ana dizini
PROJECT_ROOT = Path(__file__).parent.absolute()

# Renkli output için
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}[ADIM {step_num}] {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def run_command(command, cwd=None, description=""):
    """Komutu çalıştır ve sonucu döndür"""
    print(f"{Colors.YELLOW}> {command}{Colors.RESET}")
    if cwd:
        print(f"  Dizin: {cwd}")
    print()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            text=True
        )
        print_success(f"{description} tamamlandı!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} başarısız! (Exit code: {e.returncode})")
        return False

def step1_export_model():
    """Adım 1: YOLOv8 modelini TFLite INT8 formatına export et"""
    print_step(1, "YOLOv8 Model Export (TFLite INT8)")
    
    command = "yolo export model=yolov8n.pt format=tflite imgsz=256 int8=True"
    return run_command(command, cwd=PROJECT_ROOT, description="Model export")

def step2_quantization():
    """Adım 2: TFLite Quantization"""
    print_step(2, "TFLite Quantization")
    
    quant_dir = PROJECT_ROOT / "yolov8_quantization"
    
    if not quant_dir.exists():
        print_error(f"Dizin bulunamadı: {quant_dir}")
        return False
    
    command = "python tflite_quant.py --config-name user_config_quant.yaml"
    return run_command(command, cwd=quant_dir, description="Quantization")

def step3_deployment():
    """Adım 3: STM32N6 Deployment"""
    print_step(3, "STM32N6 Deployment")
    
    od_dir = PROJECT_ROOT / "object_detection"
    
    if not od_dir.exists():
        print_error(f"Dizin bulunamadı: {od_dir}")
        return False
    
    command = "python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_yolov8_config.yaml"
    return run_command(command, cwd=od_dir, description="Deployment")

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}   ST Object Detection Pipeline{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"\nProje dizini: {PROJECT_ROOT}\n")
    
    steps = [
        ("Model Export", step1_export_model),
        ("Quantization", step2_quantization),
        ("Deployment", step3_deployment),
    ]
    
    results = []
    
    for name, step_func in steps:
        success = step_func()
        results.append((name, success))
        
        if not success:
            print_error(f"\n{name} adımı başarısız oldu! Pipeline durduruluyor.")
            break
    
    # Özet
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}   ÖZET{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    for name, success in results:
        status = f"{Colors.GREEN}✓ Başarılı{Colors.RESET}" if success else f"{Colors.RED}✗ Başarısız{Colors.RESET}"
        print(f"  {name}: {status}")
    
    print()
    
    # Tüm adımlar başarılı mı?
    all_success = all(success for _, success in results)
    if all_success:
        print_success("Tüm adımlar başarıyla tamamlandı!")
    else:
        print_error("Bazı adımlar başarısız oldu.")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
