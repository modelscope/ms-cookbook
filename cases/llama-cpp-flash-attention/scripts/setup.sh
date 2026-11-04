#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${PROJECT:-$(dirname -- "$SCRIPT_DIR")}"
mkdir -p "$PROJECT"/{cache,cuda12,models,logs,results}
cd "$PROJECT"

MODEL_URL='https://www.modelscope.cn/models/Abiray/Qwen3.8-27B-Q4_K_M-GGUF/resolve/master/Qwen3.8-27B-Q4_K_M.gguf'
MODEL_SHA='6a96cc760fc65cc6b9ea7f1922e3ff8b2a48c09f209456f23bbae9ef7032c867'
SOURCE_URL='https://github.com/ggml-org/llama.cpp/archive/refs/tags/b10430.tar.gz'
SOURCE_SHA='c93fdbe93170b1cf93027e1a945c66a70bcdfbd272eeedbe8c90afe0a5d55e1'

aria2c -x 8 -s 8 -k 1M -c --file-allocation=none -d models -o Qwen3.8-27B-Q4_K_M.gguf "$MODEL_URL"
printf '%s  %s\n' "$MODEL_SHA" models/Qwen3.8-27B-Q4_K_M.gguf | sha256sum -c -
aria2c -x 8 -s 8 -k 1M -c --file-allocation=none -d cache -o llama-b10430-official.tar.gz "$SOURCE_URL"
printf '%s  %s\n' "$SOURCE_SHA" cache/llama-b10430-official.tar.gz | sha256sum -c -
tar -xzf cache/llama-b10430-official.tar.gz

python3 -m pip install --target "$PROJECT/cuda12" \
  nvidia-cuda-nvcc-cu12==12.4.131 \
  nvidia-cuda-runtime-cu12==12.4.127 \
  nvidia-cublas-cu12==12.4.5.8

for spec in \
  'cuda_nvcc 12.4.131' \
  'cuda_cudart 12.4.127' \
  'cuda_cccl 12.4.127'; do
  read -r component version <<< "$spec"
  name="${component}-linux-x86_64-${version}-archive"
  url="https://developer.download.nvidia.com/compute/cuda/redist/${component}/linux-x86_64/${name}.tar.xz"
  aria2c -x 8 -s 8 -k 1M -c --file-allocation=none -d cache -o "${name}.tar.xz" "$url"
  tar -xJf "cache/${name}.tar.xz" -C cuda12
done

CUDA_ROOT="$PROJECT/cuda12/cuda_nvcc-linux-x86_64-12.4.131-archive"
for source in \
  "$PROJECT/cuda12/cuda_cudart-linux-x86_64-12.4.127-archive" \
  "$PROJECT/cuda12/cuda_cccl-linux-x86_64-12.4.127-archive" \
  "$PROJECT/cuda12/nvidia/cublas"; do
  cp -a "$source/include/." "$CUDA_ROOT/include/"
  if [[ -d "$source/lib" ]]; then cp -a "$source/lib/." "$CUDA_ROOT/lib/"; fi
done
ln -sfn lib "$CUDA_ROOT/lib64"
export LD_LIBRARY_PATH="$CUDA_ROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cmake -S llama.cpp-b10430 -B build-cuda12 \
  -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=86 \
  -DCMAKE_CUDA_COMPILER="$CUDA_ROOT/bin/nvcc" -DCUDAToolkit_ROOT="$CUDA_ROOT" \
  -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$CUDA_ROOT/lib" \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
cmake --build build-cuda12 --target llama-server -j 4 2>&1 | tee logs/build-cuda12.log
"$PROJECT/build-cuda12/bin/llama-server" --help >/dev/null
printf 'Build ready: %s\n' "$PROJECT/build-cuda12/bin/llama-server"
