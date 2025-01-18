import argparse
import os
import glob
import numpy as np

import pretty_midi
import mir_eval

# Импортируем MusicApp для транскрипции
from omnizart.music import app as mapp


def midi_to_notes(midi_path):
    """
    Загружает MIDI-файл с помощью pretty_midi и возвращает списки:
    intervals: массив формы (N, 2) с начальными и конечными временами N нот
    pitches: массив с высотами нот (числовое значение MIDI-pitch)
    """
    pm = pretty_midi.PrettyMIDI(midi_path)
    intervals = []
    pitches = []
    for instrument in pm.instruments:
        # Если нужно, можно дополнительно проверять instrument.is_drum
        # или отфильтровывать инструменты по каналам, но для фортепиано
        # обычно предполагается, что в файле 1-2 инструмента без перкуссии.
        for note in instrument.notes:
            intervals.append([note.start, note.end])
            pitches.append(note.pitch)
    return np.array(intervals), np.array(pitches)


def evaluate_transcription(ref_midi, est_midi,
                           onset_tolerance=0.05,
                           offset_ratio=0.2,
                           offset_min_tolerance=0.05):
    """
    Сравнивает эталонный MIDI-файл (ref_midi) с оценочным (est_midi)
    и возвращает метрики (Precision, Recall, F-measure и т.д.).

    Параметры onset_tolerance, offset_ratio и offset_min_tolerance
    можно настраивать в зависимости от требуемой точности определения
    начала и конца ноты.
    """
    ref_intervals, ref_pitches = midi_to_notes(ref_midi)
    est_intervals, est_pitches = midi_to_notes(est_midi)

    # Если в одном из файлов нет нот, mir_eval.transcription.evaluate может бросать ошибки.
    # Поэтому стоит проверить и обработать случай пустых списков.
    if len(ref_intervals) == 0 and len(est_intervals) == 0:
        # Если нет ни одной ноты ни в эталоне, ни в предсказании, метрики можно засчитать как 1.0
        return {
            "Precision": 1.0,
            "Recall":    1.0,
            "F-measure": 1.0
        }
    if len(ref_intervals) == 0 and len(est_intervals) > 0:
        # Если в эталоне ноты отсутствуют, а в предсказании есть,
        # precision = 0, recall не определён (можно считать 0), F=0.
        return {
            "Precision": 0.0,
            "Recall":    0.0,
            "F-measure": 0.0
        }
    if len(ref_intervals) > 0 and len(est_intervals) == 0:
        # Если в предсказании нет нот, а в эталоне есть,
        # precision = 0, recall=0, F=0.
        return {
            "Precision": 0.0,
            "Recall":    0.0,
            "F-measure": 0.0
        }

    # Используем функцию для подсчёта метрик из mir_eval
    scores = mir_eval.transcription.evaluate(
        ref_intervals, ref_pitches,
        est_intervals, est_pitches,
        onset_tolerance=onset_tolerance,
        offset_ratio=offset_ratio,
        offset_min_tolerance=offset_min_tolerance
    )

    # Из результатов выбираем основные метрики
    return {
        "Precision": scores["Precision"],
        "Recall":    scores["Recall"],
        "F-measure": scores["F-measure"]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Скрипт для оценки качества транскрипции фортепиано модели Omnizart"
    )
    parser.add_argument("model_path", type=str, help="Путь к модели Omnizart.")
    parser.add_argument("dataset_dir", type=str, help="Директория с .wav/.mid файлами-бенчмарком.")
    args = parser.parse_args()

    model_path = args.model_path
    dataset_dir = args.dataset_dir

    transcriber = mapp.MusicApp()
    transcriber.load_model(model_path)

    wav_files = glob.glob(os.path.join(dataset_dir, "*.wav"))

    metrics_list = []

    for wav_path in wav_files:
        base_name = os.path.splitext(os.path.basename(wav_path))[0]
        ref_mid_path = os.path.join(dataset_dir, base_name + ".mid")

        if not os.path.exists(ref_mid_path):
            print(f"[Предупреждение] Для {wav_path} не найден {ref_mid_path}. Пропуск.")
            continue

        print(f"Транскрибируем {wav_path}...")

        est_pm = transcriber.transcribe(wav_path, output=None, model_file=model_path)
        est_mid_path = os.path.join(dataset_dir, base_name + "_transcribed.mid")
        est_pm.write(est_mid_path)

        # Считаем метрики
        scores = evaluate_transcription(ref_mid_path, est_mid_path)

        metrics_list.append(scores)
        print(f"Metrics for {base_name}:", scores)

        if os.path.exists(est_mid_path):
            os.remove(est_mid_path)

    # Подсчитаем средние метрики по всем файлам
    if len(metrics_list) == 0:
        print("Нет файлов для оценки или не найдены пары .wav/.mid.")
        return

    avg_precision = np.mean([m["Precision"] for m in metrics_list])
    avg_recall = np.mean([m["Recall"] for m in metrics_list])
    avg_fmeasure = np.mean([m["F-measure"] for m in metrics_list])

    print("\n=== Итоговые средние метрики по датасету ===")
    print(f"Precision: {avg_precision:.4f}")
    print(f"Recall:    {avg_recall:.4f}")
    print(f"F-measure: {avg_fmeasure:.4f}")


if __name__ == "__main__":
    main()
